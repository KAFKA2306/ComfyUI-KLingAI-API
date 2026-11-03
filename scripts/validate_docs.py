#!/usr/bin/env python3
"""docsの必須メタデータ・タグ・日本語見出し・内部リンクを検査する。"""
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"id", "title", "kind", "status", "updated", "tags", "related", "sources"}
JP = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")


def validate(root=ROOT):
    files = sorted((root / "docs").rglob("*.md"))
    errors, seen = [], set()
    if not files or root / "docs/README.md" not in files:
        return ["docs/README.md がありません"]
    for path in files:
        rel = path.relative_to(root).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            errors.append(f"{rel}: YAMLメタデータがありません")
            continue
        end = lines.index("---", 1)
        fields = {}
        for line in lines[1:end]:
            m = re.fullmatch(r"([a-z_]+): (.+)", line)
            if not m or m[1] in fields:
                errors.append(f"{rel}: 不正な項目か重複です: {line}")
                continue
            try:
                fields[m[1]] = json.loads(m[2])
            except json.JSONDecodeError:
                errors.append(f"{rel}: JSON互換のYAML値にしてください: {line}")
        if FIELDS - fields.keys():
            errors.append(f"{rel}: 必須項目不足: {sorted(FIELDS - fields.keys())}")
            continue
        ident = fields["id"]
        if not isinstance(ident, str) or not re.fullmatch(r"[a-z][a-z0-9-]+", ident) or ident in seen:
            errors.append(f"{rel}: idが不正か重複しています")
        else:
            seen.add(ident)
        if not isinstance(fields["title"], str) or not JP.search(fields["title"]):
            errors.append(f"{rel}: titleは日本語にしてください")
        expected = "index" if rel == "docs/README.md" else ("design" if rel.startswith("docs/design/") else "knowledge" if rel.startswith("docs/knowledge/") else None)
        if fields["kind"] != expected or fields["status"] not in ("active", "reference"):
            errors.append(f"{rel}: kind・status・配置先が不正です")
        try:
            if not isinstance(fields["updated"], str):
                raise ValueError
            date.fromisoformat(fields["updated"])
        except ValueError:
            errors.append(f"{rel}: updatedは日付文字列にしてください")
        tags = fields["tags"]
        if not isinstance(tags, list) or len(tags) < 2 or any(not isinstance(t, str) or not t.strip() for t in tags) or len(set(tags)) != len(tags):
            errors.append(f"{rel}: tagsは重複しない2件以上の文字列にしてください")
        for key in ("related", "sources"):
            values = fields[key]
            if not isinstance(values, list) or any(not isinstance(x, str) for x in values):
                errors.append(f"{rel}: {key}は文字列配列にしてください")
                continue
            for value in values:
                if key == "related" and not (root / value).is_file():
                    errors.append(f"{rel}: relatedが見つかりません: {value}")
                if key == "sources" and urlsplit(value).scheme != "https":
                    errors.append(f"{rel}: HTTPSのsourcesが必要です: {value}")
        body = "\n".join(lines[end + 1:])
        headings = re.findall(r"^# (.+)$", body, re.MULTILINE)
        if not headings or not JP.search(headings[0]):
            errors.append(f"{rel}: 日本語の見出しが必要です")
        for match in re.finditer(r"\]\(([^)]+)\)", body):
            link = match[1].split()[0]
            if link.startswith(("#", "mailto:")) or urlsplit(link).scheme:
                continue
            dest = link.split("#", 1)[0].split("?", 1)[0]
            if dest and not (path.parent / dest).resolve().is_file():
                errors.append(f"{rel}: 本文リンクの参照先なし: {link}")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        print("\n".join(failures), file=sys.stderr)
        sys.exit(1)
    print("文書メタデータ・日本語見出し・タグ・内部リンクは正常です")
