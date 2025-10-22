#!/usr/bin/env bash
set -euo pipefail

ID="${1:-add-sample-feature}"
DIR="openspec/changes/$ID"

if [[ ! -d "$DIR" ]]; then
  echo "Change folder not found: $DIR" >&2
  exit 1
fi

echo "Watching: $DIR (Ctrl+C to stop)"

validate() {
  echo "[validate] openspec validate $ID --strict"
  if openspec validate "$ID" --strict; then
    echo "[ok] Validation passed"
  else
    echo "[warn] Validation failed — common fixes:" >&2
    echo " - Ensure '## ADDED|MODIFIED|REMOVED Requirements' exists" >&2
    echo " - Use '### Requirement: <name>' for each requirement" >&2
    echo " - Add at least one '#### Scenario:' with GIVEN/WHEN/THEN" >&2
  fi
}

validate

if command -v inotifywait >/dev/null 2>&1; then
  inotifywait -mr -e modify,create,delete,move "$DIR" --format '%w%f' |
  while read -r _; do validate; done
else
  echo "inotifywait not found; using polling mode (2s)"
  LAST=""
  while true; do
    CUR=$(find "$DIR" -type f -name '*.md' -print0 | xargs -0 stat -c '%n:%Y' 2>/dev/null | sort | sha1sum | cut -d' ' -f1 || echo "none")
    if [[ "$CUR" != "$LAST" ]]; then
      LAST="$CUR"
      validate
    fi
    sleep 2
  done
fi

