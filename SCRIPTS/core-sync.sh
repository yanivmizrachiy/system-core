#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
set +H 2>/dev/null || true

CORE="$HOME/system-core"
cd "$CORE"

TITLE="${1:-SYNC}"
DID="${2:-רענון אינדקס + סטטוס + commit/push}"
NEXT="${3:-להמשיך קליטת סיכומים/ניקוי כפילויות}"
BLOCKERS="${4:-אין}"

# 1) refresh inbox index
IDX="$("$CORE/SCRIPTS/inbox-index.sh")"

# 2) snapshot status
STF="$("$CORE/SCRIPTS/core-status.sh")"

# 3) log to RULES (single source)
"$CORE/SCRIPTS/core-log.sh" "SYSTEM" "$TITLE" "$DID; נוצר: $IDX ; נוצר: $STF" "$NEXT" "$BLOCKERS"

# 4) git sync
git add -A >/dev/null 2>&1 || true
git commit -m "system-core: $TITLE ($(date -Iseconds))" >/dev/null 2>&1 || true
git push >/dev/null 2>&1 || true

echo "✅ core-sync done"
echo "IDX: $IDX"
echo "ST:  $STF"
