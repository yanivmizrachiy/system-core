#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
set +H 2>/dev/null || true
CORE="$HOME/system-core"
cd "$CORE"
TS="$(date -Iseconds)"
FN="STATE/status-$TS.txt"
{
  echo "____ SYSTEM-CORE STATUS ____"
  echo "Timestamp: $TS"
  echo ""
  echo "-- git remotes --"
  git remote -v 2>/dev/null || echo "(no git remote)"
  echo ""
  echo "-- git branch --"
  git branch --show-current 2>/dev/null || true
  echo ""
  echo "-- git log (last 5) --"
  git --no-pager log --oneline -5 2>/dev/null || true
  echo ""
  echo "-- git status --"
  git status -sb 2>/dev/null || true
} > "$FN"
echo "$FN"
