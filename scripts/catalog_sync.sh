#!/usr/bin/env bash
# 収集台帳の永続保存。キャッシュは正本ではない。
set -euo pipefail

BRANCH="main"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
mkdir -p .cache
git fetch --no-tags origin "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"
git show "refs/remotes/origin/${BRANCH}:data/workflow_registry.json" > .cache/candidate.json
git show "refs/remotes/origin/${BRANCH}:data/workflow_registry.json.sha256" > .cache/candidate.json.sha256

uv run --locked python -m gwp.state verify --catalog .cache/candidate.json
uv run --locked python -m gwp.discovery sync \
  --catalog .cache/candidate.json \
  --max-repos "${MAX_REPOS:-12}" \
  --discovery-pages "${DISCOVERY_PAGES:-1}" \
  --inspect-limit "${INSPECT_LIMIT:-50}"

bash scripts/catalog_publish.sh .cache/candidate.json
