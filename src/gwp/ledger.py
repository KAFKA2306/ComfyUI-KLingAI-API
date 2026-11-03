"""制作・採用・モデル・生成物・公開記録を出典付きで一元管理するCLI。"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from gwp.state import atomic_save, canonical, checksum, load_catalog

WRITABLE = ("projects", "adoptions", "models", "dependencies", "environments",
            "jobs", "assets", "publications", "knowledge", "rights")
ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN = {"password", "token", "secret", "api_key", "private_key",
             "authorization", "cookie", "session_key"}
JOB_STATES = ("planned", "submission_unknown", "submitted", "running",
              "succeeded", "failed", "partial", "cancelled", "not_found")
PUB_STATES = ("draft", "upload_unknown", "submitted", "reported",
              "verified", "unpublished", "removed")
TRANSITIONS = {
    "planned": {"submission_unknown", "cancelled"},
    "submission_unknown": {"submitted", "not_found", "failed", "cancelled"},
    "submitted": {"running", "succeeded", "failed", "partial", "not_found"},
    "running": {"succeeded", "failed", "partial", "cancelled", "not_found"},
    "partial": {"running", "succeeded", "failed", "cancelled"},
    "not_found": {"submitted", "failed", "cancelled"},
    "failed": set(),
    "succeeded": set(),
    "cancelled": set(),
}


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def require_id(value):
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise ValueError("IDは英数字・_-. : の128文字以内にしてください")
    return value


def require_url(value, label):
    parsed = urlparse(value) if isinstance(value, str) else None
    if not parsed or parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError(label + "には認証情報を含まないHTTPS URLが必要です")


def prevent_secrets(value):
    """公開リポジトリに認証情報を誤記録しない。"""
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN:
                raise ValueError("台帳へ秘密情報を保存できません: " + str(key))
            prevent_secrets(item)
    elif isinstance(value, list):
        for item in value:
            prevent_secrets(item)


def validate_record(catalog, kind, identifier, record):
    if kind not in WRITABLE:
        raise ValueError("対象区分が不正です")
    require_id(identifier)
    if not isinstance(record, dict) or not record:
        raise ValueError("記録は空ではないJSON objectが必要です")
    prevent_secrets(record)
    for field in ("tags", "mission_ids", "evidence_urls", "depends_on"):
        if field in record and (not isinstance(record[field], list) or
                                any(not isinstance(x, str) or not x for x in record[field])):
            raise ValueError(field + "は文字列の配列です")
    for url in record.get("evidence_urls", []):
        require_url(url, "根拠")
    for ref in record.get("depends_on", []):
        if ":" not in ref:
            raise ValueError("参照は区分:IDで記録してください")
        section, entity = ref.split(":", 1)
        if section not in catalog or not entity:
            raise ValueError("参照の区分が不正です: " + ref)
    if kind == "adoptions":
        source = record.get("artifact_id")
        if source not in catalog["artifacts"]:
            raise ValueError("存在しない出典Workflowは採用できません")
        observed = catalog["artifacts"][source]
        for field in ("blob_sha", "commit_sha"):
            if record.get(field) != observed.get(field):
                # 最新版以外を採用する場合も履歴に含まれる固定SHAなら許可する。
                if not any(rev.get(field) == record.get(field)
                           for rev in observed.get("revisions", []) if isinstance(rev, dict)):
                    raise ValueError("採用対象は収集履歴に存在する固定版にしてください: " + field)
        if not record.get("project_id") or not record.get("mission_ids"):
            raise ValueError("採用先の案件と領域を指定してください")
    if kind == "jobs":
        state = record.get("state")
        if state not in JOB_STATES:
            raise ValueError("ジョブの状態が不正です")
        if not isinstance(record.get("workflow_sha256"), str) or not SHA256.fullmatch(record["workflow_sha256"]):
            raise ValueError("ジョブには固定WorkflowのSHA-256が必要です")
        if not record.get("target") or not record.get("client_id"):
            raise ValueError("二重実行防止のため制作先とclient_idが必要です")
        if state in ("submitted", "running", "succeeded", "partial") and not record.get("prompt_id"):
            raise ValueError("送信済みジョブにはprompt_idが必要です")
    if kind == "assets":
        if not isinstance(record.get("sha256"), str) or not SHA256.fullmatch(record["sha256"]):
            raise ValueError("生成素材にはSHA-256が必要です")
        if not isinstance(record.get("bytes"), int) or record["bytes"] <= 0:
            raise ValueError("生成素材のサイズが不正です")
        if not record.get("storage_uri") or not record.get("depends_on"):
            raise ValueError("生成素材には保管先と入力への依存が必要です")
    if kind == "publications":
        state = record.get("state")
        if state not in PUB_STATES:
            raise ValueError("公開状態が不正です")
        if not record.get("platform") or not record.get("project_id"):
            raise ValueError("公開先と制作案件が必要です")
        if state == "verified":
            require_url(record.get("url"), "公開物")
            if not record.get("verified_at") or not record.get("evidence_urls") or not record.get("verification_method"):
                raise ValueError("公開済み扱いにはURL・日時・確認方法・一次証拠を指定してください")
        if state == "removed" and not record.get("evidence_urls"):
            raise ValueError("非公開化には確認した根拠URLが必要です")
    if kind == "rights":
        if not record.get("subject_ref") or not record.get("license") or not record.get("evidence_urls"):
            raise ValueError("権利は対象・ライセンス・一次根拠を版ごとに登録してください")
    if kind == "knowledge":
        if not record.get("claim") or not record.get("evidence_urls"):
            raise ValueError("知識には再利用できる結論と一次根拠を指定してください")
    return record


def put(catalog, kind, identifier, value, *, change_kind="append", actor="local"):
    validate_record(catalog, kind, identifier, value)
    if change_kind not in ("append", "correction"):
        raise ValueError("変更種別はappendまたはcorrectionです")
    existing = catalog[kind].get(identifier)
    if existing == value:
        return None
    if kind == "jobs" and existing:
        previous = existing["state"]
        current = value["state"]
        if current != previous and current not in TRANSITIONS.get(previous, set()):
            raise ValueError("ジョブの不正な状態遷移です: " + previous + " -> " + current)
        if existing.get("client_id") != value.get("client_id"):
            raise ValueError("同じジョブIDでclient_idを変えて再実行してはいけません")
    if existing and change_kind == "append":
        # 既存行の訂正は明示する。過去版はイベントに保存する。
        raise ValueError("既存IDの修正は--change-kind correctionを指定してください")
    event_id = str(uuid.uuid4())
    catalog["events"][event_id] = {
        "entity": kind + ":" + identifier,
        "kind": "correction" if existing else "created",
        "observed_at": timestamp(),
        "actor": actor,
        "before_sha256": checksum(existing) if existing is not None else None,
        "after_sha256": checksum(value),
        "before": existing,
        "after": value,
        "evidence_urls": value.get("evidence_urls", []),
    }
    catalog[kind][identifier] = value
    return event_id


def lineage(catalog, ref):
    """指定記録から遡る原典と、派生作品・公開先への波及範囲。"""
    if ":" not in ref:
        raise ValueError("区分:ID形式の参照を指定してください")
    all_records = {section + ":" + key: value for section, rows in catalog.items()
                   if isinstance(rows, dict) and section not in ("search_progress", "content_index", "events")
                   for key, value in rows.items()}
    forward = {}
    backward = {}
    for name, row in all_records.items():
        dependencies = row.get("depends_on", []) if isinstance(row, dict) else []
        if isinstance(row, dict) and row.get("artifact_id"):
            dependencies = [*dependencies, "artifacts:" + row["artifact_id"]]
        if isinstance(row, dict) and row.get("project_id"):
            dependencies = [*dependencies, "projects:" + row["project_id"]]
        forward[name] = dependencies
        for previous in dependencies:
            backward.setdefault(previous, []).append(name)

    def follow(edges):
        visited, stack = set(), [ref]
        while stack:
            current = stack.pop()
            for next_ref in edges.get(current, []):
                if next_ref not in visited and next_ref != ref:
                    visited.add(next_ref)
                    stack.append(next_ref)
        return sorted(visited)

    return {"target": ref, "sources": follow(forward),
            "affected": follow(backward), "exists": ref in all_records}


def query(catalog, section, text="", tags=(), missions=(), kind="", gpu=""):
    if section not in catalog or not isinstance(catalog[section], dict):
        raise ValueError("検索区分がありません")
    out = []
    for identifier, row in catalog[section].items():
        if not isinstance(row, dict):
            continue
        haystack = json.dumps(row, ensure_ascii=False, sort_keys=True).casefold()
        if text and text.casefold() not in haystack:
            continue
        if tags and not all(tag in row.get("tags", []) for tag in tags):
            continue
        if missions and not all(mission in row.get("mission_ids", []) for mission in missions):
            continue
        if kind and kind != row.get("format", row.get("kind", "")):
            continue
        if gpu and gpu.casefold() not in haystack:
            continue
        out.append({"id": identifier, **row})
    return out


def hash_file(path):
    result = hashlib.sha256()
    size = 0
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
            size += len(block)
    return {"sha256": result.hexdigest(), "bytes": size}


def main(argv=None):
    parser = argparse.ArgumentParser(description="採用・実行・素材・公開の変更履歴を一元管理")
    parser.add_argument("command", choices=("put", "get", "query", "lineage", "hash-file"))
    parser.add_argument("--catalog", type=Path, default=Path("data/workflow_registry.json"))
    parser.add_argument("--section", choices=WRITABLE + ("artifacts", "repositories"))
    parser.add_argument("--id")
    parser.add_argument("--payload", type=Path)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--change-kind", choices=("append", "correction"), default="append")
    parser.add_argument("--actor", default="local")
    parser.add_argument("--term", default="")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--mission", action="append", default=[])
    parser.add_argument("--format", default="")
    parser.add_argument("--gpu", default="")
    args = parser.parse_args(argv)
    if args.command == "hash-file":
        if not args.file:
            parser.error("hash-fileは--fileが必要です")
        print(json.dumps(hash_file(args.file), ensure_ascii=False))
        return
    catalog = load_catalog(args.catalog, allow_missing=False)
    if args.command in ("put", "get", "lineage") and not args.id:
        parser.error("--idが必要です")
    if args.command == "lineage":
        output = lineage(catalog, args.id)
    elif args.command == "query":
        if not args.section:
            parser.error("--sectionが必要です")
        output = query(catalog, args.section, args.term, args.tag,
                       args.mission, args.format, args.gpu)
    elif args.command == "get":
        if not args.section:
            parser.error("--sectionが必要です")
        output = catalog[args.section][args.id]
    else:
        if not args.section or args.section not in WRITABLE or not args.payload:
            parser.error("putには編集可能な--sectionと--payloadが必要です")
        input_data = json.loads(args.payload.read_text(encoding="utf-8"))
        event_id = put(catalog, args.section, args.id, input_data,
                       change_kind=args.change_kind, actor=args.actor)
        if event_id:
            atomic_save(args.catalog, catalog)
        output = {"event_id": event_id, "record_id": args.id,
                  "unchanged": event_id is None}
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
