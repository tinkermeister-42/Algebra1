#!/bin/bash
set -euo pipefail

BOOK_DIR="_book"
DEPLOY_BRANCH="gh-pages"
ORIGINAL_DIR="$(pwd)"
DRY_RUN=false
: "${SIGN_COMMITS:=false}"   # set SIGN_COMMITS=true to sign the deploy commit

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "DRY RUN: No files will be deleted, committed, or pushed."
fi

# ---------- Preconditions ----------
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "Not a git repo."; exit 1; }
ABS_REPO_ROOT="$(git rev-parse --show-toplevel)"
ABS_BOOK_DIR="$ABS_REPO_ROOT/$BOOK_DIR"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "You have uncommitted changes. Commit or stash before deploying."
  exit 1
fi

# ---------- Build ----------
echo "Building the book..."
quarto render --to html

[[ -d "$BOOK_DIR" ]] || { echo "'$BOOK_DIR' not found after render."; exit 1; }

# ---------- Temp worktree ----------
git worktree prune || true
TEMP_WORKTREE_DIR="$(mktemp -d -t gh-pages-XXXXXX)"
ABS_TEMP_DIR="$(cd "$TEMP_WORKTREE_DIR" && pwd -P)"

# Sanity: never let temp dir equal repo root or book dir
if [[ "$ABS_TEMP_DIR" == "$ABS_REPO_ROOT" || "$ABS_TEMP_DIR" == "$ABS_BOOK_DIR" ]]; then
  echo "TEMP_WORKTREE_DIR resolves to a dangerous path. Aborting."
  exit 1
fi

echo "Preparing worktree for $DEPLOY_BRANCH..."
if git show-ref --verify --quiet "refs/heads/$DEPLOY_BRANCH"; then
  git worktree add "$ABS_TEMP_DIR" "$DEPLOY_BRANCH"
elif git ls-remote --exit-code --heads origin "$DEPLOY_BRANCH" >/dev/null 2>&1; then
  # -B creates the local branch at the remote tip; without it the worktree is on a
  # detached HEAD and the push at the end has no "$DEPLOY_BRANCH" ref to push.
  git worktree add -B "$DEPLOY_BRANCH" "$ABS_TEMP_DIR" "origin/$DEPLOY_BRANCH"
else
  # First deploy: create orphan branch
  git worktree add --detach "$ABS_TEMP_DIR"
  (
    cd "$ABS_TEMP_DIR"
    git switch --orphan "$DEPLOY_BRANCH"
    rm -rf ./* .[^.]* 2>/dev/null || true
    echo "# $(basename "$ABS_REPO_ROOT") pages" > README.md
    git add README.md
    git -c commit.gpgsign=${SIGN_COMMITS} commit -m "Initialize $DEPLOY_BRANCH"
    [[ "$DRY_RUN" == true ]] || git push -u origin "$DEPLOY_BRANCH" || true
  )
  git worktree remove "$ABS_TEMP_DIR" --force
  git worktree add "$ABS_TEMP_DIR" "$DEPLOY_BRANCH"
fi

# Sync to remote tip to avoid divergence
(
  cd "$ABS_TEMP_DIR"
  git fetch origin "$DEPLOY_BRANCH" || true
  git reset --hard "origin/$DEPLOY_BRANCH" || true
  git config core.autocrlf false
  if [[ ! -f .gitattributes ]]; then
    printf '* text=auto eol=lf\nsite_libs/** -text\n' > .gitattributes
    git add .gitattributes
    git -c commit.gpgsign=${SIGN_COMMITS} commit -m "chore: pin LF endings on gh-pages" || true
  fi
)

# ---------- Clean & copy ----------
echo "Cleaning old files..."
if [[ "$DRY_RUN" == true ]]; then
  echo "DRY RUN: would clean '$ABS_TEMP_DIR' and copy from '$BOOK_DIR'"
else
  find "$ABS_TEMP_DIR" -mindepth 1 \
    ! -name '.git' ! -name '.github' ! -name '.nojekyll' \
    ! -name 'CNAME' ! -name '.gitattributes' \
    -exec rm -rf {} + 2>/dev/null || true
  (cd "$BOOK_DIR"; tar -cf - .) | (cd "$ABS_TEMP_DIR"; tar -xpf -)
  touch "$ABS_TEMP_DIR/.nojekyll"
fi

# ---------- Commit & push ----------
echo "Committing changes..."
cd "$ABS_TEMP_DIR"
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  if [[ "$DRY_RUN" == true ]]; then
    echo "DRY RUN: would commit and push with --force-with-lease"
  else
    git -c commit.gpgsign=${SIGN_COMMITS} commit -m "Deploy updated book"
    echo "Pushing to $DEPLOY_BRANCH..."
    git push --force-with-lease origin "$DEPLOY_BRANCH"
  fi
fi

# ---------- Cleanup ----------
cd "$ORIGINAL_DIR"
[[ "$DRY_RUN" == true ]] || git worktree remove "$ABS_TEMP_DIR" --force || true

echo "Deployment complete."