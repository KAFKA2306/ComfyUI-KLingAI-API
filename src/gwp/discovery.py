"""公開Workflowの出典と改訂履歴を記録する収集器。第三者のコードは実行しない。"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

BASE = "https://api.github.com"
CANDIDATE_SUFFIXES = (".json", ".jsonc", ".png", ".webp", ".workflow")
MODEL_KEYS = {"ckpt_name", "unet_name", "lora_name", "vae_name", "control_net_name",
              "clip_name", "model_name", "diffusion_model", "filename"}


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")



def new_catalog():
    return {"schema_version": 1, "repositories": {}, "artifacts": {},
            "discoveries": {}, "evidence": {}, "feeds": {}, "references": {},
            "search_progress": {}}


def load_catalog(path):
    if not path.exists():
        return new_catalog()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported catalog schema")
    return data


def atomic_save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    tmp.replace(path)


def workflow_details(data):
    """Classify without rejecting unknown, invalid, or incomplete JSON."""
    if isinstance(data, dict) and isinstance(data.get("definitions"), dict) and \
            "subgraphs" in data["definitions"]:
        kind = "blueprint"
    elif isinstance(data, dict) and isinstance(data.get("nodes"), list):
        kind = "workflow-ui"
    elif isinstance(data, dict) and data and all(
            isinstance(value, dict) and "class_type" in value for value in data.values()):
        kind = "workflow-api"
    else:
        kind = "json-unclassified"
    nodes = set()
    models = set()

    def visit(obj):
        if isinstance(obj, dict):
            name = obj.get("class_type") or obj.get("type")
            if isinstance(name, str):
                nodes.add(name)
            for key, value in obj.items():
                if key.lower() in MODEL_KEYS and isinstance(value, str):
                    models.add(value)
                if isinstance(value, (dict, list)):
                    visit(value)
        elif isinstance(obj, list):
            for value in obj:
                if isinstance(value, (dict, list)):
                    visit(value)

    visit(data)
    return {"kind": kind, "node_types": sorted(nodes), "model_references": sorted(models)}


class API:
    def __init__(self, token=None, opener=urlopen):
        self.token = token
        self.opener = opener

    def json(self, url):
        if not url.startswith(("https://api.github.com/", "https://huggingface.co/api/",
                               "https://civitai.com/api/v1/")):
            raise ValueError("Unexpected API origin")
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "workflow-source-registry"}
        if self.token and url.startswith(BASE + "/"):
            headers["Authorization"] = "Bearer " + self.token
        with self.opener(Request(url, headers=headers), timeout=40) as response:
            return json.load(response)


def walk_tree(api, repo, ref):
    """Retrieve complete file list, descending non-recursively when GitHub truncates."""
    prefix = BASE + "/repos/" + repo + "/git/trees/"
    first = api.json(prefix + quote(ref, safe="") + "?recursive=1")
    if not first.get("truncated"):
        return [item for item in first["tree"] if item.get("type") == "blob"]
    stack = [("", ref)]
    result = []
    while stack:
        parent, sha = stack.pop()
        page = api.json(prefix + quote(sha, safe=""))
        for item in page.get("tree", []):
            path = parent + item["path"]
            if item.get("type") == "tree":
                stack.append((path + "/", item["sha"]))
            elif item.get("type") == "blob":
                result.append({**item, "path": path})
    return result


def record_file(catalog, repo, commit_sha, item, stamp):
    path = item["path"]
    if not path.lower().endswith(CANDIDATE_SUFFIXES):
        return False
    item_id = "github:" + repo.lower() + ":" + path
    previous = catalog["artifacts"].get(item_id)
    blob = item["sha"]
    if previous is not None and previous["blob_sha"] == blob:
        return False
    raw_url = "https://raw.githubusercontent.com/" + repo + "/" + commit_sha + "/" + quote(path, safe="/")
    entry = dict(previous or {})
    history = entry.get("revisions", [])
    history.append({"commit_sha": commit_sha, "blob_sha": blob, "observed_at": stamp})
    entry.update({"id": item_id, "source": "github:" + repo.lower(), "path": path,
                  "source_url": "https://github.com/" + repo + "/blob/" + commit_sha + "/" + quote(path, safe="/"),
                  "raw_url": raw_url, "blob_sha": blob, "commit_sha": commit_sha,
                  "size_bytes": item.get("size"), "revisions": history,
                  "format": "json-uninspected" if path.lower().endswith((".json", ".jsonc"))
                  else "possible-embedded-workflow-uninspected",
                  "inspection": "pending" if path.lower().endswith((".json", ".jsonc")) else "requires-image-metadata-decoder"})
    # Changed content must be re-inspected, but its earlier revisions are preserved.
    entry.pop("node_types", None)
    entry.pop("model_references", None)
    catalog["artifacts"][item_id] = entry
    return True


def inspect_pending(api, catalog, limit):
    # Inspection is best effort; candidates remain recorded even if unreadable.
    inspected = 0
    for artifact in catalog["artifacts"].values():
        if inspected >= limit:
            break
        if artifact.get("inspection") != "pending":
            continue
        repo = artifact["source"].removeprefix("github:")
        path = artifact["path"]
        if artifact.get("size_bytes") and artifact["size_bytes"] > 1000000:
            artifact["inspection"] = "large-file-pending"
            continue
        url = BASE + "/repos/" + repo + "/contents/" + quote(path, safe="/") + "?" + urlencode({"ref": artifact["commit_sha"]})
        try:
            response = api.json(url)
            if response.get("encoding") != "base64":
                artifact["inspection"] = "unsupported-encoding"
                continue
            import base64
            raw = base64.b64decode(response["content"])
            details = workflow_details(json.loads(raw.decode("utf-8")))
            artifact["format"] = details.pop("kind")
            artifact.update(details)
            artifact["inspection"] = "complete"
        except (ValueError, UnicodeError, KeyError, TypeError) as exc:
            artifact["inspection"] = "invalid-or-nonworkflow-json"
            artifact["inspection_error"] = type(exc).__name__
        except (HTTPError, URLError, TimeoutError) as exc:
            # Retryable. Do not discard this candidate or turn an API outage into invalid JSON.
            artifact["last_inspection_error"] = str(exc)[:250]
        inspected += 1
    return inspected



def discover_organizations(api, catalog, organizations):
    """組織の公開リポジトリを列挙し、失敗を消滅と取り違えない。"""
    for organization in organizations:
        for page in range(1, 101):
            url = BASE + "/orgs/" + quote(organization, safe="") + "/repos?" + urlencode(
                {"per_page": 100, "page": page, "type": "public"})
            try:
                repos = api.json(url)
            except (HTTPError, URLError, TimeoutError, ValueError, TypeError) as exc:
                catalog["search_progress"]["org:" + organization + ":error"] = str(exc)[:250]
                break
            if not isinstance(repos, list):
                catalog["search_progress"]["org:" + organization + ":error"] = "invalid_response"
                break
            for repository in repos:
                full = repository.get("full_name")
                if not full:
                    continue
                key = full.lower()
                row = catalog["discoveries"].setdefault(key, {
                    "repo": full, "discovered_via": [], "url": repository.get("html_url") or
                    "https://github.com/" + full})
                tag = "organization:" + organization
                if tag not in row["discovered_via"]:
                    row["discovered_via"].append(tag)
            if len(repos) < 100:
                break


def discover_github(api, catalog, queries, pages):
    for query in queries:
        progress = catalog["search_progress"].get(query, 1)
        for page_no in range(progress, progress + pages):
            url = BASE + "/search/repositories?" + urlencode({"q": query, "sort": "updated",
                                                                "order": "desc", "per_page": 100,
                                                                "page": page_no})
            try:
                response = api.json(url)
            except (HTTPError, URLError, TimeoutError) as exc:
                catalog["search_progress"][query + ":error"] = str(exc)[:250]
                break
            items = response.get("items", [])
            for item in items:
                repo = item.get("full_name")
                if repo:
                    key = repo.lower()
                    catalog["discoveries"].setdefault(key, {"repo": repo, "discovered_via": [], "url": item.get("html_url")})
                    via = catalog["discoveries"][key]["discovered_via"]
                    if query not in via:
                        via.append(query)
            # GitHub search exposes at most 1,000 entries per query. Keep a provenance note.
            catalog["search_progress"][query + ":total_count"] = response.get("total_count", 0)
            catalog["search_progress"][query] = page_no + 1 if items and len(items) == 100 and page_no < 10 else 1
            if len(items) < 100 or page_no >= 10:
                break


def discover_feed(api, catalog, feed):
    feed_id = feed["id"]
    state = catalog["feeds"].setdefault(feed_id, {"kind": feed["kind"], "url": feed["url"], "items": {}})
    try:
        # Metadata discovery only. We do not claim model-card files are Workflow JSON.
        page = api.json(feed["url"])
        items = page if isinstance(page, list) else page.get("items", [])
        for item in items:
            identifier = item.get("id") or item.get("modelId")
            if identifier is None:
                continue
            state["items"][str(identifier)] = {
                "id": identifier, "url": item.get("url") or
                ("https://huggingface.co/" + str(identifier) if feed["kind"] == "huggingface-models"
                 else "https://civitai.com/models/" + str(identifier)),
                "revision": item.get("sha") or item.get("updatedAt") or item.get("lastModified"),
                "kind": feed["kind"], "collection": "metadata-only"}
        state.pop("error", None)
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        state["error"] = str(exc)[:300]


def sync(api, catalog, settings, max_repos=12, discovery_pages=1, inspect_limit=50):
    stamp = now_utc()
    for ref in settings.get("reference_sources", []):
        catalog["references"][ref["id"]] = ref
    for entry in settings.get("github_repos", []):
        catalog["discoveries"].setdefault(entry.lower(), {
            "repo": entry, "discovered_via": ["configured-seed"],
            "url": "https://github.com/" + entry})
    discover_organizations(api, catalog, settings.get("github_organizations", []))
    discover_github(api, catalog, settings.get("github_queries", []), discovery_pages)
    # Round-robin across all discoveries; no popularity score or exclusion policy.
    queue = sorted(catalog["discoveries"].values(),
                   key=lambda item: (catalog["repositories"].get(item["repo"].lower(), {}).get("last_scanned_at", ""),
                                     item["repo"].lower()))
    for candidate in queue[:max_repos]:
        repo = candidate["repo"]
        key = repo.lower()
        state = catalog["repositories"].setdefault(key, {"repo": repo, "url": "https://github.com/" + repo})
        try:
            meta = api.json(BASE + "/repos/" + repo)
            branch = meta["default_branch"]
            commit = api.json(BASE + "/repos/" + repo + "/commits/" + quote(branch, safe=""))
            sha = commit["sha"]
            if sha != state.get("head_sha"):
                files = walk_tree(api, repo, branch)
                updated = 0
                for item in files:
                    if record_file(catalog, repo, sha, item, stamp):
                        updated += 1
                state["candidate_files_seen"] = sum(p["path"].lower().endswith(CANDIDATE_SUFFIXES) for p in files)
                state["files_seen"] = len(files)
                state["new_or_changed_artifacts"] = updated
                state["head_sha"] = sha
            state["last_scanned_at"] = stamp
            state["default_branch"] = branch
            state.pop("last_error", None)
            # Source-level issue references. This bounded window is explicitly marked.
            try:
                issues = api.json(BASE + "/repos/" + repo + "/issues?state=all&sort=updated&per_page=30")
                for issue in issues:
                    if "pull_request" in issue:
                        continue
                    i = "github:" + key + "#" + str(issue["number"])
                    catalog["evidence"][i] = {"source": "github:" + key, "url": issue["html_url"],
                        "title": issue["title"], "state": issue["state"], "updated_at": issue["updated_at"],
                        "kind": "issue-reference", "scope": "repository-not-specific-workflow"}
                state["evidence_coverage"] = "latest-30-issues-only; older issues not yet indexed"
            except (HTTPError, URLError, TimeoutError) as exc:
                state["evidence_error"] = str(exc)[:200]
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError) as exc:
            state["last_error"] = str(exc)[:300]
            state["last_scanned_at"] = stamp
    inspect_pending(api, catalog, inspect_limit)
    for feed in settings.get("metadata_feeds", []):
        discover_feed(api, catalog, feed)
    return catalog


def search(catalog, query):
    words = query.casefold().split()
    for item in catalog["artifacts"].values():
        haystack = " ".join([item.get("path", ""), item.get("source", ""),
                              item.get("format", ""), *item.get("node_types", []),
                              *item.get("model_references", [])]).casefold()
        if all(word in haystack for word in words):
            yield item



def labels_for(item, categories):
    """検索用分類。品質や動作確認とは無関係。"""
    terms = " ".join([
        item.get("path", ""), item.get("source", ""),
        " ".join(item.get("node_types", [])),
        " ".join(item.get("model_references", [])),
    ]).casefold()
    return [category["title"] for category in categories if any(
        word.casefold() in terms for word in category["keywords"])]


def export_catalog(catalog, categories, format="csv"):
    """未分類を含む全候補を日本語のCSVまたはJSONに書き出す。"""
    rows = []
    for item in sorted(catalog["artifacts"].values(),
                       key=lambda x: (x.get("source", ""), x.get("path", ""))):
        rows.append({
            "ID": item["id"],
            "出典": item.get("source", ""),
            "ファイル": item.get("path", ""),
            "原典URL": item.get("source_url", ""),
            "コミット": item.get("commit_sha", ""),
            "ファイルSHA": item.get("blob_sha", ""),
            "形式": item.get("format", "未確認"),
            "確認状態": item.get("inspection", "未確認"),
            "用途候補（未検証）": "／".join(labels_for(item, categories)) or "未分類",
            "利用条件": "未確認",
        })
    if format == "json":
        return json.dumps({"schema_version": 1, "count": len(rows), "items": rows},
                          ensure_ascii=False, indent=2) + "\n"
    if format != "csv":
        raise ValueError("未対応の出力形式")
    buffer = io.StringIO(newline="")
    fields = ["ID", "出典", "ファイル", "原典URL", "コミット", "ファイルSHA",
              "形式", "確認状態", "用途候補（未検証）", "利用条件"]
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return "\ufeff" + buffer.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Source-preserving Workflow Registry")
    parser.add_argument("command", nargs="?", choices=("sync", "search", "stats", "export"), default="sync")
    parser.add_argument("--catalog", type=Path, default=Path("data/workflow_registry.json"))
    parser.add_argument("--sources", type=Path, default=Path("config/workflow_sources.json"))
    parser.add_argument("--max-repos", type=int, default=12)
    parser.add_argument("--discovery-pages", type=int, default=1)
    parser.add_argument("--inspect-limit", type=int, default=50)
    parser.add_argument("--term", default="")
    parser.add_argument("--format", choices=("csv", "json"), default="csv")
    args = parser.parse_args(argv)
    catalog = load_catalog(args.catalog)
    if args.command == "sync":
        settings = json.loads(args.sources.read_text(encoding="utf-8"))
        sync(API(os.environ.get("GITHUB_TOKEN")), catalog, settings,
             max_repos=args.max_repos, discovery_pages=args.discovery_pages,
             inspect_limit=args.inspect_limit)
        atomic_save(args.catalog, catalog)
    elif args.command == "export":
        settings = json.loads(args.sources.read_text(encoding="utf-8"))
        sys.stdout.write(export_catalog(catalog, settings.get("categories", []), args.format))
    elif args.command == "search":
        for item in search(catalog, args.term):
            print(json.dumps({"source_url": item["source_url"], "format": item["format"],
                              "path": item["path"], "inspection": item["inspection"]},
                             ensure_ascii=False))
    elif args.command == "stats":
        print(json.dumps({"sources": len(catalog["repositories"]),
                          "discovered_repositories": len(catalog["discoveries"]),
                          "artifacts": len(catalog["artifacts"]),
                          "issue_references": len(catalog["evidence"]),
                          "metadata_feeds": len(catalog["feeds"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
