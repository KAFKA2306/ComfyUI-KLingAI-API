"""収集台帳の完全性、移行、復旧、競合統合。外部ライブラリ不要。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path
from urllib.parse import quote

SCHEMA_VERSION = 2
SECTIONS = ("repositories", "artifacts", "discoveries", "evidence", "feeds",
            "references", "search_progress", "content_index", "events",
            "projects", "adoptions", "models", "dependencies", "environments",
            "jobs", "assets", "publications", "knowledge", "rights")
IDENTITY_FIELDS = {"id", "source", "path", "repo", "url"}
LIST_UNION = {"revisions", "discovered_via", "node_types", "model_references",
              "aliases", "tags", "mission_ids", "source_urls", "evidence_urls",
              "overflows"}


def empty_catalog():
    return {"schema_version": SCHEMA_VERSION, **{name: {} for name in SECTIONS}}


def canonical(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def checksum(data):
    return hashlib.sha256(canonical(data)).hexdigest()


def migrate(data):
    if not isinstance(data, dict) or data.get("schema_version") not in (1, 2):
        raise ValueError("未対応または不正な収集台帳スキーマです")
    copy = deepcopy(data)
    copy["schema_version"] = SCHEMA_VERSION
    for section in SECTIONS:
        if section not in copy:
            copy[section] = {}
        if not isinstance(copy[section], dict):
            raise ValueError("台帳の区分が不正です: " + section)
    for key, item in copy["artifacts"].items():
        if not isinstance(key, str) or not isinstance(item, dict):
            raise ValueError("候補ID/データが不正です")
        if "revisions" in item and not isinstance(item["revisions"], list):
            raise ValueError("改訂履歴が不正です: " + key)
    return copy


def load_catalog(path, *, allow_missing=True, require_checksum=False):
    path = Path(path)
    if not path.exists():
        if allow_missing:
            return empty_catalog()
        raise FileNotFoundError(path)
    raw = path.read_bytes()
    marker = path.with_name(path.name + ".sha256")
    if require_checksum and not marker.exists():
        raise ValueError("SHA-256検証ファイルがありません: " + str(marker))
    if marker.exists() and marker.read_text(encoding="ascii").strip() != hashlib.sha256(raw).hexdigest():
        raise ValueError("保存済みSHA-256が一致しません。復旧が必要です: " + str(path))
    try:
        return migrate(json.loads(raw))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("JSONの破損を検出しました: " + str(path)) from error


def _sync_directory(path):
    if os.name != "nt":
        descriptor = os.open(str(path), os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _durable_write(path, raw):
    """同じディレクトリで一時ファイルを同期してから置換する。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="." + path.name + "-", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(raw)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
        _sync_directory(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_save(path, data, *, expected_sha256=None, preserve=True):
    """旧版を保持し、読み込み時点から他の書き込みがあれば上書きしない。"""
    path = Path(path)
    migrated = migrate(data)
    raw = canonical(migrated)
    if expected_sha256 is not None:
        current = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if current != expected_sha256:
            raise RuntimeError("他のプロセスが台帳を更新しました。mergeで統合してください")
    if path.exists() and preserve:
        # 検証できた旧版だけを退避。壊れた台帳を正常バックアップへ上書きしない。
        previous = load_catalog(path, allow_missing=False)
        old_raw = path.read_bytes()
        if checksum(previous) or previous:
            backup = path.with_name(path.name + ".bak")
            _durable_write(backup, old_raw)
            _durable_write(backup.with_name(backup.name + ".sha256"),
                           (hashlib.sha256(old_raw).hexdigest() + "\n").encode("ascii"))
    _durable_write(path, raw)
    _durable_write(path.with_name(path.name + ".sha256"),
                   (hashlib.sha256(raw).hexdigest() + "\n").encode("ascii"))
    return hashlib.sha256(raw).hexdigest()


def _merge_value(left, right, field=None):
    if isinstance(left, dict) and isinstance(right, dict):
        result = deepcopy(left)
        for key, value in right.items():
            if key not in result:
                result[key] = deepcopy(value)
            elif key in IDENTITY_FIELDS and result[key] != value:
                # 原典URLの移転は別名・別URLとして記録する。改竄しない。
                if key in ("source", "path", "id", "repo"):
                    raise ValueError("同一IDで出典識別子が競合しています: " + key)
                result[key] = value
            else:
                result[key] = _merge_value(result[key], value, key)
        if "revisions" in result and isinstance(result["revisions"], list):
            latest = max((r for r in result["revisions"] if isinstance(r, dict)),
                         key=lambda r: (r.get("observed_at", ""), r.get("commit_sha", "")),
                         default=None)
            if latest and "blob_sha" in latest:
                result["blob_sha"] = latest["blob_sha"]
                result["commit_sha"] = latest.get("commit_sha", result.get("commit_sha"))
                if result.get("source", "").startswith("github:") and result.get("path"):
                    repository = result["source"].removeprefix("github:")
                    commit = result["commit_sha"]
                    name = quote(result["path"], safe="/")
                    result["raw_url"] = (
                        "https://raw.githubusercontent.com/" + repository + "/" + commit + "/" + name)
                    result["source_url"] = (
                        "https://github.com/" + repository + "/blob/" + commit + "/" + name)
        return result
    if isinstance(left, list) and isinstance(right, list) and field in LIST_UNION:
        out = deepcopy(left)
        seen = {json.dumps(row, sort_keys=True, ensure_ascii=False) for row in out}
        for row in right:
            marker = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if marker not in seen:
                out.append(deepcopy(row))
                seen.add(marker)
        if field == "revisions":
            out.sort(key=lambda row: (row.get("observed_at", ""), row.get("commit_sha", ""))
                     if isinstance(row, dict) else ("", ""))
        return out
    # 単一の値は上書きより非空を優先。タイムスタンプがあるレコードは下で補正。
    return deepcopy(right if right is not None and right != "" else left)


def _merge_item(left, right):
    if not isinstance(left, dict) or not isinstance(right, dict):
        return _merge_value(left, right)
    a_time = left.get("last_scanned_at") or left.get("updated_at") or ""
    b_time = right.get("last_scanned_at") or right.get("updated_at") or ""
    if a_time > b_time:
        left, right = right, left
    merged = _merge_value(left, right)
    # 一度の巡回失敗は過去の成功時点と収集件数を消してはいけない。
    successes = [record for record in (left, right)
                 if record.get("last_success_at") and record.get("last_success_sha")]
    if successes:
        latest = max(successes, key=lambda record: (
            record["last_success_at"], record["last_success_sha"]))
        merged["last_success_at"] = latest["last_success_at"]
        merged["last_success_sha"] = latest["last_success_sha"]
    return merged


def merge_catalog(current, incoming):
    """2台のPCや再試行の結果を単調に統合。登録済みの候補を消さない。"""
    a, b = migrate(current), migrate(incoming)
    out = deepcopy(a)
    for section in SECTIONS:
        for key, row in b[section].items():
            if key not in out[section]:
                out[section][key] = deepcopy(row)
            elif section == "content_index" and isinstance(out[section][key], list) and isinstance(row, list):
                out[section][key] = _merge_value(
                    out[section][key], row, "source_urls")
            elif section == "artifacts" and isinstance(out[section][key], dict) and isinstance(row, dict):
                left = out[section][key]
                def revision_time(item):
                    return max((rev.get("observed_at", "") for rev in item.get("revisions", [])
                                if isinstance(rev, dict)), default="")
                if revision_time(left) > revision_time(row):
                    out[section][key] = _merge_item(row, left)
                else:
                    out[section][key] = _merge_item(left, row)
            else:
                out[section][key] = _merge_item(out[section][key], row)
    for section in SECTIONS:
        if len(out[section]) < max(len(a[section]), len(b[section])):
            raise AssertionError("統合で記録が消失しました")
    # 旧版の台帳にはcontent_indexが存在しない場合がある。
    # 復元した候補と過去改訂をBlob SHAから必ず引けるように再構築する。
    for artifact_id, artifact in out["artifacts"].items():
        blobs = {artifact.get("blob_sha")}
        blobs.update(rev.get("blob_sha") for rev in artifact.get("revisions", [])
                     if isinstance(rev, dict))
        for blob in blobs:
            if not isinstance(blob, str) or not blob:
                continue
            references = out["content_index"].setdefault(blob, [])
            if not isinstance(references, list):
                raise ValueError("内容索引の形式が不正です: " + blob)
            if artifact_id not in references:
                references.append(artifact_id)
    # 制作台帳の訂正履歴はイベントが正本。同時編集では双方を残したうえで
    # 最新の確定イベントから表示用の現在値を再構成する。
    latest = {}
    for event_id, event in out["events"].items():
        if not isinstance(event, dict) or not isinstance(event.get("entity"), str):
            continue
        entity = event["entity"]
        if ":" not in entity or "after" not in event:
            continue
        section, identifier = entity.split(":", 1)
        if section not in ("projects", "adoptions", "models", "dependencies",
                           "environments", "jobs", "assets", "publications",
                           "knowledge", "rights"):
            continue
        candidate = (event.get("observed_at", ""), event_id)
        if entity not in latest or candidate > latest[entity][0]:
            latest[entity] = (candidate, section, identifier, event["after"])
    for _, (_, section, identifier, row) in latest.items():
        out[section][identifier] = deepcopy(row)
    return migrate(out)


def health(current, previous=None):
    now = migrate(current)
    counts = {name: len(now[name]) for name in SECTIONS}
    missing = {}
    if previous is not None:
        old = migrate(previous)
        for name in SECTIONS:
            removed = sorted(set(old[name]) - set(now[name]))
            if removed:
                missing[name] = removed[:30]
    return {"schema_version": SCHEMA_VERSION, "counts": counts,
            "missing_previous_keys": missing,
            "status": "ok" if not missing else "data-loss-detected"}


def restore(path, backup):
    """破損した本体を隔離し、検証済み版から復旧する。"""
    source = Path(backup)
    candidate = load_catalog(source, allow_missing=False, require_checksum=True)
    path = Path(path)
    previous = None
    if path.exists():
        try:
            previous = load_catalog(path, allow_missing=False)
        except ValueError:
            quarantine = path.with_name(path.name + ".corrupt")
            if quarantine.exists():
                raise FileExistsError("隔離先が既に存在します: " + str(quarantine))
            path.replace(quarantine)
            marker = path.with_name(path.name + ".sha256")
            if marker.exists():
                marker.replace(quarantine.with_name(quarantine.name + ".sha256"))
        else:
            # 正常な現行版に古いバックアップを上書きするとIDと改訂履歴が失われる。
            candidate = merge_catalog(previous, candidate)
    atomic_save(path, candidate, preserve=True)
    return health(candidate, previous)


def backup(path, destination):
    """独立した保存先に検証可能なスナップショットを作る。既存版は上書きしない。"""
    path, destination = Path(path), Path(destination)
    current = load_catalog(path, allow_missing=False, require_checksum=True)
    digest = checksum(current)
    dest = destination / (digest + ".json")
    if dest.exists():
        if checksum(load_catalog(dest, allow_missing=False)) != digest:
            raise ValueError("既存バックアップが破損しています")
        return dest
    atomic_save(dest, current, preserve=False)
    if checksum(load_catalog(dest, allow_missing=False)) != digest:
        raise IOError("バックアップの再検証に失敗しました")
    return dest


def main(argv=None):
    parser = argparse.ArgumentParser(description="収集台帳の保全・検証・競合統合")
    parser.add_argument("command", choices=("verify", "merge", "restore", "init", "status", "backup"))
    parser.add_argument("--catalog", type=Path, default=Path("data/workflow_registry.json"))
    parser.add_argument("--other", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.command == "init":
        if args.catalog.exists():
            raise FileExistsError("既存台帳は上書きしません")
        atomic_save(args.catalog, empty_catalog())
        result = health(load_catalog(args.catalog))
    elif args.command == "restore":
        if args.other is None:
            parser.error("restoreには--otherが必要です")
        result = restore(args.catalog, args.other)
    elif args.command == "backup":
        if args.output is None:
            parser.error("backupには--output（別媒体のディレクトリ）が必要です")
        result = {"backup": str(backup(args.catalog, args.output))}
    elif args.command == "merge":
        if args.other is None or args.output is None:
            parser.error("mergeには--otherと--outputが必要です")
        combined = merge_catalog(load_catalog(args.catalog, allow_missing=False),
                                 load_catalog(args.other, allow_missing=False))
        if args.output.resolve() == args.catalog.resolve():
            atomic_save(args.output, combined)
        else:
            atomic_save(args.output, combined, preserve=False)
        result = health(combined)
    else:
        current = load_catalog(args.catalog, allow_missing=False,
                               require_checksum=(args.command == "verify"))
        previous = load_catalog(args.other, allow_missing=False) if args.other else None
        result = health(current, previous)
        if result["status"] != "ok":
            raise SystemExit("過去の台帳に存在したIDが欠損しています: " +
                             json.dumps(result["missing_previous_keys"], ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
