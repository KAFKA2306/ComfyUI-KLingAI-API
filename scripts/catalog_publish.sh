#!/usr/bin/env bash
# 収集結果・制作履歴を同じcatalog正本へ統合し、競合時も再試行する。
set -euo pipefail

if [[ "$#" -ne 1 || ! -f "$1" ]]; then
  echo "使い方: bash scripts/catalog_publish.sh <更新済み台帳.json>" >&2
  exit 2
fi
INPUT="$(realpath -- "$1")"
if [[ ! -f "${INPUT}.sha256" ]]; then
  echo "SHA-256検証ファイルがありません: ${INPUT}.sha256" >&2
  exit 1
fi

BRANCH="${CATALOG_BRANCH:-catalog}"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
uv run --locked python -m gwp.state verify --catalog "$INPUT"

mkdir -p .cache
git fetch --no-tags origin "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"
WORKTREE="$(mktemp -d "$ROOT/.cache/catalog-publish.XXXXXXXX")"
cleanup() {
  git worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
  rmdir "$WORKTREE" >/dev/null 2>&1 || true
}
trap cleanup EXIT
git worktree add --detach "$WORKTREE" "refs/remotes/origin/${BRANCH}" >/dev/null

# ローカルのGit設定は変更しない。コミット単位で実行者を指定する。
if [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
  AUTHOR_NAME="github-actions[bot]"
  AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com"
else
  AUTHOR_NAME="${GIT_AUTHOR_NAME:-$(git config user.name || true)}"
  AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-$(git config user.email || true)}"
  if [[ -z "$AUTHOR_NAME" || -z "$AUTHOR_EMAIL" ]]; then
    echo "Gitのuser.nameとuser.emailを設定してください" >&2
    exit 1
  fi
fi

for attempt in 1 2 3 4 5; do
  git fetch --no-tags origin "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"
  git -C "$WORKTREE" reset --hard "refs/remotes/origin/${BRANCH}" >/dev/null
  uv run --locked python -m gwp.state merge \
    --catalog "$WORKTREE/data/workflow_registry.json" \
    --other "$INPUT" \
    --output "$WORKTREE/data/workflow_registry.json"
  uv run --locked python -m gwp.state verify \
    --catalog "$WORKTREE/data/workflow_registry.json"
  git -C "$WORKTREE" add data/workflow_registry.json data/workflow_registry.json.sha256
  if git -C "$WORKTREE" diff --cached --quiet; then
    echo "正本に未反映の差分はありません"
    exit 0
  fi
  git -C "$WORKTREE" -c user.name="$AUTHOR_NAME" -c user.email="$AUTHOR_EMAIL" \
    commit -m "data: 台帳の変更を競合統合して保全" >/dev/null
  if git -C "$WORKTREE" push origin "HEAD:refs/heads/${BRANCH}"; then
    echo "catalog正本へ反映しました"
    exit 0
  fi
  echo "更新競合のため再統合します (${attempt}/5)" >&2
done
echo "5回の再試行後も保存できませんでした。入力台帳はそのまま保持しました" >&2
exit 1
