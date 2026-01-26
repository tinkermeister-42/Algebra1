#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: count_callouts.sh path1 [path2 ...]"
  exit 2
fi

CALLS=(
  answers
  answer
  objectives
  vocab
  real-world
  remember
  you-try
  you-try-m
  think
  gotcha
  note
)

printf "file"
for c in "${CALLS[@]}"; do
  printf "\t%s" "$c"
done
printf "\n"

files=()
for root in "$@"; do
  if [[ -d "$root" ]]; then
    while IFS= read -r -d '' f; do
      files+=("$f")
    done < <(find "$root" -type f -name '*.qmd' -print0 2>/dev/null || true)
  elif [[ -f "$root" && "$root" == *.qmd ]]; then
    files+=("$root")
  fi
done

if [[ ${#files[@]} -eq 0 ]]; then
  echo "No .qmd files found under: $*"
  exit 1
fi

IFS=$'\n' files_sorted=($(printf "%s\n" "${files[@]}" | sort))
unset IFS

for file in "${files_sorted[@]}"; do
  printf "%s" "$file"

  for c in "${CALLS[@]}"; do
    count=$(
      (grep -E "^[[:space:]]*:::[[:space:]]*(\{[[:space:]]*\.?$c\b|\.$c\b|$c\b)" "$file" || true) \
        | wc -l \
        | tr -d ' '
    )
    printf "\t%s" "$count"
  done

  printf "\n"
done
