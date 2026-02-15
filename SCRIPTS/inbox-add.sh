#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
set +H 2>/dev/null || true

CORE="$HOME/system-core"
cd "$CORE"

CAT="${1:-}"
TITLE="${2:-}"
[ -n "$CAT" ] && [ -n "$TITLE" ] || { echo "Usage: inbox-add <CATEGORY> <TITLE>"; exit 2; }

TS="$(date -Iseconds)"
SAFE_TITLE="$(printf "%s" "$TITLE" | tr " /:\t" "____" | tr -cd "[:alnum:]_א-ת-")"
FN="INBOX/${TS}__${CAT}__${SAFE_TITLE}.md"

echo "# $TITLE" > "$FN"
echo "" >> "$FN"
echo "- Timestamp: $TS" >> "$FN"
echo "- Category: $CAT" >> "$FN"
echo "" >> "$FN"
echo "## תוכן" >> "$FN"
echo "" >> "$FN"
echo "הדבק כאן את הסיכום (החל מהשורה הבאה):" >> "$FN"
echo "" >> "$FN"

echo "$FN"
