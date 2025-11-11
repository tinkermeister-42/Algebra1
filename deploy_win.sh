#!/bin/bash
set -euo pipefail

BOOK_DIR="_book"
DEPLOY_BRANCH="gh-pages"
ORIGINAL_DIR="$(pwd)"
DRY_RUN=false
: "${SIGN_COMMITS:=false}"   # set SIGN_COMMITS=true to sign the deploy commit

# ---------- Parse flags ----------
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "🔍 DRY RUN: No files will be deleted, committed, or pushed."
fi

# ---------- Preconditions & safety checks ----------
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "❌ Not a git repo."; exit 1; }
ABS_REPO_ROOT="$(git rev-parse --show-toplevel)"
ABS_BOOK_DIR="$ABS_REPO_ROOT/$BOOK_DIR"

# Require clean working tree (outside temp worktree)
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "❌ You have uncommitted changes in this repo. Commit/stash before deploying."
  exit 1
fi

# Build first (fail early if render breaks)
echo "📘 Building the book..."
quarto render --to html

if [[ ! -d "$BOOK_DIR" ]]; then
  echo "❌ '$BOOK_DIR' not found after render."
  exit 1
fi

# ---------- Prepare a unique temp worktree ----------
# Preemptively clear stale worktree admin dirs that Windows may lock
if [[ -d .git/worktrees ]]; then
  for d in .git/worktrees/gh-pages* .git/worktrees/gh-pages-temp*; do
    [[ -e "$d" ]] && rm -rf "$d" || true
  done
fi
git worktree prune || true

# Unique temp dir (absolute path)
TEMP_WORKTREE_DIR="$(mktemp -d -t gh-pages-XXXXXX)"
if [[ ! -d "$TEMP_WORKTREE_DIR" ]]; then
  echo "❌ Failed to create temp worktree directory."
  exit 1
fi

# Sanity: never let temp dir equal repo root or book dir
ABS_TEMP_DIR="$(cd "$TEMP_WORKTREE_DIR" && pwd -P)"
if [[ "$ABS_TEMP_DIR" == "$ABS_REPO_ROOT" || "$ABS_TEMP_DIR" == "$ABS_BOOK_DIR" ]]; then
  echo "❌ TEMP_WORKTREE_DIR resolves to a dangerous path. Aborting."
  exit 1
fi

echo "🌿 Preparing temp worktree for $DEPLOY_BRANCH..."
# Attach to existing branch (local or remote) or create orphan
if git show-ref --verify --quiet "refs/heads/$DEPLOY_BRANCH"; then
  git worktree add "$ABS_TEMP_DIR" "$DEPLOY_BRANCH"
elif git ls-remote --exit-code --heads origin "$DEPLOY_BRANCH" >/dev/null 2>&1; then
  git worktree add "$ABS_TEMP_DIR" "origin/$DEPLOY_BRANCH"
else
  # Safe first-deploy path
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

# Sync to remote tip to avoid merges
(
  cd "$ABS_TEMP_DIR"
  git fetch origin "$DEPLOY_BRANCH" || true
  git reset --hard "origin/$DEPLOY_BRANCH" || true

  # ---------- Pin EOL behavior and quiet CRLF warnings ----------
  git config core.autocrlf false
  if [[ ! -f .gitattributes ]]; then
    cat > .gitattributes <<'EOF'
* text=auto eol=lf
site_libs/** -text
EOF
    git add .gitattributes
    git -c commit.gpgsign=${SIGN_COMMITS} commit -m "chore: pin LF endings on gh-pages" || true
  fi
)

# ---------- Clean target (preserve important files) ----------
echo "🧹 Cleaning old files (preserve .git, .github, .nojekyll, CNAME, .gitattributes)..."
if [[ "$DRY_RUN" == true ]]; then
  echo "DRY RUN: would delete everything in '$ABS_TEMP_DIR' except .git, .github, .nojekyll, CNAME, .gitattributes"
else
  find "$ABS_TEMP_DIR" -mindepth 1 \
    ! -name '.git' \
    ! -name '.github' \
    ! -name '.nojekyll' \
    ! -name 'CNAME' \
    ! -name '.gitattributes' \
    -exec rm -rf {} + 2>/dev/null
fi

# ---------- Copy new site (via tar, preserves dotfiles) ----------
echo "📥 Copying new files to $DEPLOY_BRANCH branch (via tar)..."
if [[ "$DRY_RUN" == true ]]; then
  echo "DRY RUN: would tar from '$BOOK_DIR' and extract into '$ABS_TEMP_DIR'"
else
  (
    cd "$BOOK_DIR"
    tar -cf - .
  ) | (
    cd "$ABS_TEMP_DIR"
    tar -xpf -
  )
fi

# Ensure .nojekyll exists (don’t let GitHub run Jekyll)
[[ "$DRY_RUN" == true ]] || touch "$ABS_TEMP_DIR/.nojekyll"

# ---------- Commit & Push (lease-protected) ----------
echo "📦 Committing changes..."
cd "$ABS_TEMP_DIR"
git add -A
if git diff --cached --quiet; then
  echo "⚠️ No changes to commit"
else
  if [[ "$DRY_RUN" == true ]]; then
    echo "DRY RUN: would commit and push with --force-with-lease"
  else
    git -c commit.gpgsign=${SIGN_COMMITS} commit -m "Deploy updated book"
    echo "🚀 Pushing to $DEPLOY_BRANCH (force-with-lease)"
    git push --force-with-lease origin "$DEPLOY_BRANCH"
  fi
fi

# ---------- Cleanup ----------
echo "🧹 Cleaning up temp worktree..."
cd "$ORIGINAL_DIR"
if [[ "$DRY_RUN" == true ]]; then
  echo "DRY RUN: would remove worktree at '$ABS_TEMP_DIR'"
else
  git worktree remove "$ABS_TEMP_DIR" --force || true
  # Best-effort cleanup of any lingering admin dirs
  if [[ -d .git/worktrees ]]; then
    for d in .git/worktrees/gh-pages* .git/worktrees/gh-pages-temp*; do
      [[ -e "$d" ]] && rm -rf "$d" || true
    done
  fi
fi

echo "✅ Deployment complete!"
