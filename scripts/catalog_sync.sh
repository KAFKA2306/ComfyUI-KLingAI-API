#!/usr/bin/env bash
# 収集台帳の永続保存。キャッシュは正本ではない。
set -euo pipefail

BRANCH="${CATALOG_BRANCH:-catalog}"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
mkdir -p .cache
git fetch --no-tags origin "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"
git worktree add --detach .cache/catalog "refs/remotes/origin/${BRANCH}"
cp .cache/catalog/data/workflow_registry.json .cache/candidate.json
cp .cache/catalog/data/workflow_registry.json.sha256 .cache/candidate.json.sha256

uv run --locked python -m gwp.discovery sync \
  --catalog .cache/candidate.json \
  --max-repos "${MAX_REPOS:-12}" \
  --discovery-pages "${DISCOVERY_PAGES:-1}" \
  --inspect-limit "${INSPECT_LIMIT:-50}"
uv run --locked python -m gwp.state verify --catalog .cache/candidate.json

# 先行した別PCの変更を再取得し、ID単位で統合してからGitへ反映する。
for attempt in 1 2 3 4 5; do
  git fetch --no-tags origin "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"
  git -C .cache/catalog reset --hard "refs/remotes/origin/${BRANCH}"
  uv run --locked python -m gwp.state merge \
    --catalog .cache/catalog/data/workflow_registry.json \
    --other .cache/candidate.json \
    --output .cache/catalog/data/workflow_registry.json
  git -C .cache/catalog add data/workflow_registry.json data/workflow_registry.json.sha256
  if git -C .cache/catalog diff --cached --quiet; then
    echo "台帳に差分はありません"
    exit 0
  fi
  git -C .cache/catalog config user.name "github-actions[bot]"
  git -C .cache/catalog config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git -C .cache/catalog commit -m "data: 収集台帳を保全・統合"
  if git -C .cache/catalog push origin "HEAD:refs/heads/${BRANCH}"; then
    echo "永続台帳を更新しました"
    exit 0
  fi
  echo "更新競合、再取得します (${attempt}/5)" >&2
done
echo "更新競合を5回解消できませんでした。正本は変更されていません" >&2
exit 1
