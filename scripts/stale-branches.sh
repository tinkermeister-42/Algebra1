#!/bin/bash
# List every remote branch except main and gh-pages, and say whether its work
# is already on main. Prints one delete command for the branches that are safe.
#   scripts/stale-branches.sh
# A squash merge never makes a branch's commits ancestors of main, so a branch
# counts as on main when any of these hold:
#   - it is an ancestor of main (merged the ordinary way)
#   - merging it into main would change nothing
#   - some commit on main has the branch's version of every text file it changed
set -uo pipefail
cd "$(dirname "$0")/.."
git fetch -q origin '+refs/heads/*:refs/remotes/origin/*' || exit 1
main_tree=$(git rev-parse origin/main^{tree})
safe=()
for ref in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin); do
  b=${ref#origin/}
  case "$b" in main|gh-pages|HEAD|origin) continue ;; esac
  if git merge-base --is-ancestor "$ref" origin/main; then
    safe+=("$b"); echo "on main      $b"; continue
  fi
  mb=$(git merge-base origin/main "$ref") || { echo "NO BASE      $b  (shallow clone: fetch more history)"; continue; }
  if [ "$(git merge-tree --write-tree origin/main "$ref" 2>/dev/null | head -1)" = "$main_tree" ]; then
    safe+=("$b"); echo "on main      $b"; continue
  fi
  mapfile -t files < <(git diff --name-only "$mb" "$ref" -- . ':!*.pdf' ':!*.svg' ':!*.png' ':!glossary.json')
  hit=""
  if [ ${#files[@]} -eq 0 ]; then hit="built files only"
  else
    for c in $(git rev-list --first-parent --reverse "$mb"..origin/main); do
      git diff --quiet "$c" "$ref" -- "${files[@]}" && { hit="squashed in $(git log -1 --format=%h "$c")"; break; }
    done
  fi
  if [ -n "$hit" ]; then safe+=("$b"); echo "on main      $b  ($hit)"
  else echo "CHECK        $b  ($(git log -1 --format='%cs: %s' "$ref" | cut -c1-60))"; fi
done
if [ ${#safe[@]} -gt 0 ]; then echo; echo "git push origin --delete ${safe[*]}"; fi
