#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
set +H 2>/dev/null || true
CORE="$HOME/system-core"
cd "$CORE"
catg="${1:-}"; title="${2:-}"; did="${3:-}"; nxt="${4:-}"; blockers="${5:-}"
[ -n "$catg" ] && [ -n "$title" ] && [ -n "$did" ] && [ -n "$nxt" ] || { echo "Usage: core-log <CAT> <TITLE> <DID> <NEXT> [BLOCKERS]"; exit 2; }
TS="$(date -Iseconds)"
DAY="$(date +%F)"
KEY="[[CORE_LOG:$DAY|$catg|$title]]"
touch RULES.md
grep -Fq "$KEY" RULES.md 2>/dev/null && { echo "SKIP: already logged"; exit 0; }

{
  echo ""
  echo "---"
  echo ""
  echo "## קטגוריה: $catg"
  echo ""
  echo "### $title — $TS"
  echo "$KEY"
  echo ""
  echo "**מה בוצע**"
  echo "- $did"
  echo ""
  echo "**מה הבא**"
  echo "- $nxt"
  echo ""
  echo "**חסמים**"
  echo "- ${blockers:-אין חסמים ידועים כרגע}"
  echo ""
} >> RULES.md

printf "{ \"last_update\": \"%s\", \"category\": \"%s\", \"title\": \"%s\", \"key\": \"%s\" }\n" "$TS" "$catg" "$title" "$KEY" > STATE/last_update.json

git add RULES.md STATE/last_update.json >/dev/null 2>&1 || true
git commit -m "RULES: [$catg] $title ($TS)" >/dev/null 2>&1 || true
git push >/dev/null 2>&1 || true
echo "LOGGED: [$catg] $title"
