#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Scaffold OpenSpec change files from SpecKit templates (cross-platform).

Usage:
  ./scripts/speckit_map.sh <change-id> [capability] [--no-design] [--with-decision-log] [--with-pivot] [--force]

Args:
  <change-id>   Required, kebab-case id (e.g., add-awesome-feature)
  [capability]  Optional capability folder (default: platform)

Flags:
  --no-design         Skip creating design.md
  --with-decision-log Also create decision-log.md
  --with-pivot        Also create pivot.md
  --force             Overwrite files if they already exist

Examples:
  ./scripts/speckit_map.sh add-feature platform
  ./scripts/speckit_map.sh add-feature tooling --no-design
USAGE
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" || $# -lt 1 ]]; then
  usage
  exit 0
fi

CHANGE_ID="$1"; shift || true
CAPABILITY="${1:-platform}"
if [[ $# -ge 1 ]]; then shift; fi

NO_DESIGN=false
WITH_DECISION_LOG=false
WITH_PIVOT=false
FORCE=false

while (( "$#" )); do
  case "$1" in
    --no-design) NO_DESIGN=true; shift;;
    --with-decision-log) WITH_DECISION_LOG=true; shift;;
    --with-pivot) WITH_PIVOT=true; shift;;
    --force) FORCE=true; shift;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2;;
  esac
done

TEMPLATE_ROOT=".speckit/templates/openspec"
PROPOSAL_TPL="$TEMPLATE_ROOT/proposal-skeleton.md"
TASKS_TPL="$TEMPLATE_ROOT/tasks-skeleton.md"
DESIGN_TPL="$TEMPLATE_ROOT/design-skeleton.md"
DECISION_TPL="$TEMPLATE_ROOT/decision-log-skeleton.md"
PIVOT_TPL="$TEMPLATE_ROOT/pivot-skeleton.md"
DELTA_TPL="$TEMPLATE_ROOT/delta-spec-skeleton.md"

for f in "$PROPOSAL_TPL" "$TASKS_TPL" "$DELTA_TPL"; do
  if [[ ! -f "$f" ]]; then
    echo "Template not found: $f" >&2
    exit 1
  fi
done

CHANGE_ROOT="openspec/changes/$CHANGE_ID"
SPEC_ROOT="$CHANGE_ROOT/specs/$CAPABILITY"

mkdir -p "$SPEC_ROOT"

write_file() {
  local path="$1"; shift
  local content="$1"; shift || true
  if [[ -f "$path" && "$FORCE" != true ]]; then
    echo "File exists: $path (use --force to overwrite)" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$path")"
  printf "%s" "$content" > "$path"
}

substitute() {
  local tpl="$1"; shift
  local req_title="SpecKit Integration"
  sed -e "s/{{change_id}}/$CHANGE_ID/g" \
      -e "s/{{requirement_title}}/$req_title/g" "$tpl"
}

echo "Scaffolding OpenSpec change from SpecKit templates..."

write_file "$CHANGE_ROOT/proposal.md" "$(cat "$PROPOSAL_TPL")"
write_file "$CHANGE_ROOT/tasks.md"    "$(substitute "$TASKS_TPL")"
write_file "$SPEC_ROOT/spec.md"       "$(substitute "$DELTA_TPL")"

if [[ "$NO_DESIGN" != true && -f "$DESIGN_TPL" ]]; then
  write_file "$CHANGE_ROOT/design.md" "$(cat "$DESIGN_TPL")"
fi

if [[ "$WITH_DECISION_LOG" == true && -f "$DECISION_TPL" ]]; then
  write_file "$CHANGE_ROOT/decision-log.md" "$(cat "$DECISION_TPL")"
fi

if [[ "$WITH_PIVOT" == true && -f "$PIVOT_TPL" ]]; then
  write_file "$CHANGE_ROOT/pivot.md" "$(cat "$PIVOT_TPL")"
fi

echo "Created change at: $CHANGE_ROOT"
echo "Next: Fill proposal/tasks/specs from SpecKit outputs, then run:"
echo "  openspec validate $CHANGE_ID --strict"
echo "Optional: Maintain direction with decision-log.md and pivot.md flags"
