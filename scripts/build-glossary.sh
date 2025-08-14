#!/usr/bin/env bash

echo "[build-glossary] generating glossary.json..."

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    IS_WINDOWS=true
    ;;
  *)
    IS_WINDOWS=false
    ;;
esac

PANDOC=$(command -v pandoc 2>/dev/null)

if [[ -z "$PANDOC" && "$IS_WINDOWS" = true ]]; then
  QUARTO_PANDOC="/c/Users/jaross/AppData/Local/Programs/Quarto/bin/tools/pandoc.exe"
  if [[ -x "$QUARTO_PANDOC" ]]; then
    PANDOC="$QUARTO_PANDOC"
    echo "[build-glossary] using fallback pandoc at $PANDOC"
  fi
fi

if [[ -z "$PANDOC" ]]; then
  echo "[build-glossary] ERROR: pandoc not found!" >&2
  exit 1
fi

# Use a temporary file for output on Windows, /dev/null on Unix
if [[ "$IS_WINDOWS" = true ]]; then
  TMP_OUT="$(mktemp).json"
else
  TMP_OUT="/dev/null"
fi

echo "[build-glossary] Using pandoc executable at: $PANDOC"

"$PANDOC" glossary.qmd -t plain --lua-filter=scripts/generate-glossary-json.lua -o "$TMP_OUT"

PANDOC_EXIT_CODE=$?

# Remove temp file if on Windows
if [[ "$IS_WINDOWS" = true && -f "$TMP_OUT" ]]; then
  rm "$TMP_OUT"
fi

if [[ $PANDOC_EXIT_CODE -eq 0 ]]; then
  echo "[build-glossary] done."
else
  echo "[build-glossary] failed!" >&2
  exit 1
fi
