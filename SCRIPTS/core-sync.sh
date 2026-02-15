#!/data/data/com.termux/files/usr/bin/bash
set -e
TS=$(date -Iseconds)

echo "## Update $TS" >> RULES.md
echo "- עודכן בעקבות פעולה חדשה" >> RULES.md
echo "" >> RULES.md

git add .
git commit -m "CORE UPDATE $TS" || true
git push 2>/dev/null || true
