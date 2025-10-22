#!/usr/bin/env bash
set -euo pipefail

DEFAULT_ID="add-sample-feature"
DEFAULT_CAP="platform"

echo "OpenSpec Easy Mode"
echo "Answer a few questions. I’ll do the rest."

read -r -p "Change ID (kebab-case) [${DEFAULT_ID}]: " ID
ID=${ID:-$DEFAULT_ID}
ID=$(echo "$ID" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]]+/-/g; s/[^a-z0-9-]//g')
if [[ -z "$ID" ]]; then echo "Invalid change id" >&2; exit 1; fi

read -r -p "Capability folder [${DEFAULT_CAP}]: " CAP
CAP=${CAP:-$DEFAULT_CAP}

read -r -p "Add decision-log.md? (y/N): " DEC
read -r -p "Add pivot.md? (y/N): " PIV

ARGS=("-Id" "$ID" "-Capability" "$CAP")
[[ "$DEC" =~ ^[Yy]([Ee][Ss])?$ ]] && ARGS+=("-WithDecisionLog")
[[ "$PIV" =~ ^[Yy]([Ee][Ss])?$ ]] && ARGS+=("-WithPivot")

echo
echo "Scaffolding files..."
pwsh -NoProfile -Command "./scripts/speckit_map.ps1 $(${ARGS[@]} | sed 's/\"/\\\"/g')" 2>/dev/null || \
./scripts/speckit_map.sh "$ID" "$CAP" $([[ "$DEC" =~ ^[Yy] ]] && echo --with-decision-log) $([[ "$PIV" =~ ^[Yy] ]] && echo --with-pivot)

echo
echo "Checking your work with strict validation..."
openspec validate "$ID" --strict || true

echo
echo "All set! Open these files and fill them in:"
echo "  openspec/changes/$ID/proposal.md"
echo "  openspec/changes/$ID/tasks.md"
[[ -f "openspec/changes/$ID/design.md" ]] && echo "  openspec/changes/$ID/design.md"
[[ -f "openspec/changes/$ID/decision-log.md" ]] && echo "  openspec/changes/$ID/decision-log.md"
[[ -f "openspec/changes/$ID/pivot.md" ]] && echo "  openspec/changes/$ID/pivot.md"
echo "  openspec/changes/$ID/specs/$CAP/spec.md"

echo
echo "Next steps:"
echo "  1) Edit the files above (use Markdown preview)."
echo "  2) Run: openspec validate $ID --strict"
echo "  3) After approval and implementation: openspec archive $ID --yes"

