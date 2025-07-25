#!/bin/bash

# Generate glossary.json from glossary.md
echo "[build-glossary] generating glossary.json..."

pandoc glossary.qmd -t plain --lua-filter=scripts/generate-glossary-json.lua \
  -o /dev/null

if [[ $? -eq 0 ]]; then
  echo "[build-glossary] done."
else
  echo "[build-glossary] failed!" >&2
  exit 1
fi
