#!/usr/bin/env bash
# watch-assets.sh — Re-trigger Quarto preview when widget HTML files change.
#
# Run this in a second terminal alongside `quarto preview`:
#   ./scripts/watch-assets.sh
#
# Requires inotify-tools:
#   sudo dnf install inotify-tools

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ASSETS_DIR="$ROOT/assets"
CHAPTERS_DIR="$ROOT/chapters"

# Fallback: polling loop (used if inotifywait is unavailable)
poll_loop() {
  echo "inotifywait not found — falling back to 1-second polling."
  echo "Install inotify-tools for instant response: sudo dnf install inotify-tools"
  echo ""
  declare -A mtimes
  while true; do
    while IFS= read -r -d '' file; do
      mtime=$(stat -c '%Y' "$file" 2>/dev/null || echo 0)
      prev="${mtimes[$file]:-}"
      if [[ "$prev" != "" && "$mtime" != "$prev" ]]; then
        on_change "$file"
      fi
      mtimes["$file"]="$mtime"
    done < <(find "$ASSETS_DIR" -name "*.html" -print0)
    sleep 1
  done
}

on_change() {
  local changed="$1"
  local filename
  filename="$(basename "$changed")"
  echo "[watch] $filename changed"
  # Touch every .qmd that includes this asset file
  local found=0
  while IFS= read -r qmd; do
    echo "  → touching $(realpath --relative-to="$ROOT" "$qmd")"
    touch "$qmd"
    found=1
  done < <(grep -rl "$filename" "$CHAPTERS_DIR" 2>/dev/null || true)
  if [[ $found -eq 0 ]]; then
    echo "  (no .qmd includes $filename — nothing touched)"
  fi
}

echo "Watching $ASSETS_DIR for changes..."
echo "Run 'quarto preview' in another terminal."
echo ""

if command -v inotifywait &>/dev/null; then
  inotifywait -m -r "$ASSETS_DIR" -e close_write --format '%w%f' 2>/dev/null \
  | while IFS= read -r changed; do
      on_change "$changed"
    done
else
  poll_loop
fi
