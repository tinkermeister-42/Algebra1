#!/bin/bash
set -euo pipefail

BOOK_DIR="_book"
DEPLOY_BRANCH="gh-pages"
TEMP_WORKTREE_DIR="../gh-pages-temp"
ORIGINAL_DIR="$(pwd)"

echo "📘 Building the book..."
quarto render --to html

echo "🌿 Preparing temp worktree for $DEPLOY_BRANCH..."
rm -rf "$TEMP_WORKTREE_DIR"
git worktree prune
git worktree add "$TEMP_WORKTREE_DIR" "$DEPLOY_BRANCH"

# Make sure the worktree is exactly at the remote tip (avoids rebase)
(
  cd "$TEMP_WORKTREE_DIR"
  git fetch origin "$DEPLOY_BRANCH" || true
  git reset --hard "origin/$DEPLOY_BRANCH" || true  # ok on first deploy if branch doesn't exist yet
)

echo "🧹 Cleaning old files (preserve .git, .nojekyll, CNAME)..."
find "$TEMP_WORKTREE_DIR" -mindepth 1 \
  ! -name '.git' \
  ! -name '.nojekyll' \
  ! -name 'CNAME' \
  -exec rm -rf {} +

echo "📥 Copying new files to $DEPLOY_BRANCH branch..."
# rsync is safer than cp and handles deletions cleanly
rsync -av --delete \
  --exclude '.git' \
  --exclude '.nojekyll' \
  --exclude 'CNAME' \
  "$BOOK_DIR"/ "$TEMP_WORKTREE_DIR"/

# Re-create .nojekyll (GitHub Pages: skip Jekyll)
touch "$TEMP_WORKTREE_DIR/.nojekyll"

echo "📦 Committing changes..."
cd "$TEMP_WORKTREE_DIR"
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Deploy updated book"
  echo "🚀 Pushing to $DEPLOY_BRANCH (force-with-lease)"
  git push --force-with-lease origin "$DEPLOY_BRANCH"
else
  echo "⚠️ No changes to commit"
fi

echo "🧹 Cleaning up temp worktree..."
cd "$ORIGINAL_DIR"
git worktree remove "$TEMP_WORKTREE_DIR" --force

echo "✅ Deployment complete!"
