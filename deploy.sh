#!/bin/bash
set -e

BOOK_DIR="_book"
DEPLOY_BRANCH="gh-pages"
TEMP_WORKTREE_DIR="../gh-pages-temp"
ORIGINAL_DIR=$(pwd)

echo "📘 Building the book..."
quarto render --to html

echo "🌿 Preparing temp worktree for $DEPLOY_BRANCH..."
rm -rf $TEMP_WORKTREE_DIR
git worktree prune
git worktree add $TEMP_WORKTREE_DIR $DEPLOY_BRANCH

echo "🧹 Cleaning old files..."
find $TEMP_WORKTREE_DIR -mindepth 1 ! -name '.git' ! -name '.nojekyll' -exec rm -rf {} +

echo "📥 Copying new files to $DEPLOY_BRANCH branch..."
cp -r $BOOK_DIR/* $TEMP_WORKTREE_DIR/
touch $TEMP_WORKTREE_DIR/.nojekyll

echo "📦 Committing changes..."
cd $TEMP_WORKTREE_DIR
git add -A

# Commit if there are staged changes
if ! git diff --cached --quiet; then
  git commit -m "Deploy updated book"

  echo "🔄 Pulling remote changes (rebase)"
  git pull --rebase origin $DEPLOY_BRANCH

  echo "🚀 Pushing to $DEPLOY_BRANCH"
  git push origin $DEPLOY_BRANCH --force
else
  echo "⚠️ No changes to commit"
fi


echo "🧹 Cleaning up temp worktree..."
cd "$ORIGINAL_DIR"
git worktree remove "$TEMP_WORKTREE_DIR" --force

echo "✅ Deployment complete!"
