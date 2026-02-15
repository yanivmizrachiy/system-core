#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail; set +H 2>/dev/null || true
REPO="pdf-system"
ROOT="$HOME/$REPO"
PLAN="$HOME/system-core/STATE/repo-move-lists/2026-02-15T15:00:13+02:00/pdf-system__move-list.txt"
[ -d "$ROOT" ] || { echo "❌ missing repo dir: $ROOT"; exit 2; }
[ -f "$PLAN" ] || { echo "❌ missing plan: $PLAN"; exit 3; }

cd "$ROOT"
mkdir -p TRASH

echo "== MOVE ONLY (NO DELETE) =="
echo "REPO=$REPO"
echo "PLAN=$PLAN"
echo

n=0
while IFS= read -r rel; do
  [ -n "${rel:-}" ] || continue
  src="$ROOT/$rel"
  if [ -e "$src" ]; then
    dst="$ROOT/TRASH/$rel"
    mkdir -p "$(dirname "$dst")"
    mv -f "$src" "$dst"
    echo "MOVED: $rel"
    n=$((n+1))
  else
    echo "SKIP missing: $rel"
  fi
done < <(awk "NF" "$PLAN")

echo
echo "✅ DONE moved=$n"
