"""自律改善メモリの根拠とスキーマを検証する。"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_PATH = Path("data/agent_memory.json")
SHA = re.compile(r"[0-9a-f]{40}")


def _https(value):
    return isinstance(value, str) and urlsplit(value).scheme == "https" and bool(urlsplit(value).netloc)


def _date(value):
    try:
        return isinstance(value, str) and bool(date.fromisoformat(value))
    except ValueError:
        return False


def validate(memory):
    """必須項目・証拠・IDの一意性を検査し、エラーを返す。"""
    errors = []
    if not isinstance(memory, dict):
        return ["メモリはJSONオブジェクトにしてください"]
    if memory.get("schema_version") != 1:
        errors.append("schema_version は1にしてください")
    if memory.get("scope") != "KAFKA2306/comfyui-workflows-factory":
        errors.append("scope が対象リポジトリと一致しません")
    baseline = memory.get("baseline")
    if not isinstance(baseline, dict):
        errors.append("baseline が必要です")
    elif not (
        isinstance(baseline.get("observed_main_sha"), str)
        and SHA.fullmatch(baseline["observed_main_sha"])
        and _date(baseline.get("observed_on"))
        and _https(baseline.get("source_url"))
    ):
        errors.append("baseline のSHA、日付、根拠URLが不正です")
    ids = set()
    groups = {
        "verified_lessons": ("finding", "evidence_url", "checked_on"),
        "hypotheses": ("hypothesis", "basis_url", "checked_on", "proposed_test", "next_action"),
        "blocked_attempts": ("operation", "failure", "checked_on", "resume_when"),
    }
    for group, required in groups.items():
        rows = memory.get(group)
        if not isinstance(rows, list):
            errors.append(f"{group} は配列にしてください")
            continue
        for index, row in enumerate(rows):
            label = f"{group}[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: オブジェクトである必要があります")
                continue
            ident = row.get("id")
            if not isinstance(ident, str) or not re.fullmatch(r"[a-z][a-z0-9-]+", ident) or ident in ids:
                errors.append(f"{label}: IDが不正か重複しています")
            else:
                ids.add(ident)
            for key in required:
                if not isinstance(row.get(key), str) or not row[key].strip():
                    errors.append(f"{label}: {key} がありません")
            if not _date(row.get("checked_on")):
                errors.append(f"{label}: checked_on が不正です")
            for key in ("evidence_url", "basis_url"):
                if key in row and not _https(row[key]):
                    errors.append(f"{label}: {key} はHTTPSの根拠URLにしてください")
            if group == "hypotheses" and row.get("status") != "unverified":
                errors.append(f"{label}: 検証済みの仮説はverified_lessonsへ移してください")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description="自律改善メモリを検証する")
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args(argv)
    try:
        memory = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f"メモリの読み込みに失敗: {exc}\n")
    errors = validate(memory)
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print("自律改善メモリ: スキーマと根拠は正常です")


if __name__ == "__main__":
    main()
