#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
CORE="$HOME/system-core"
cd "$CORE"
OUT="INBOX/_index.md"
TS="$(date -Iseconds)"

{
  echo "# INBOX INDEX"
  echo ""
  echo "- Updated: $TS"
  echo ""
  echo "## קבצים (מהחדש לישן)"
  echo ""
  ls -1 INBOX 2>/dev/null | grep -v "^_index\.md$" | sort -r | while read -r f; do
    echo "- $f"
  done
  echo ""
} > "$OUT"

echo "$OUT"
