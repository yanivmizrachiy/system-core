#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
set +H 2>/dev/null || true
CORE="$HOME/system-core"
cd "$CORE"

TS="$(date -Iseconds)"
TRASH="TRASH/$TS"
mkdir -p "$TRASH"

# Only move files explicitly listed in STATE/cleanup-move-list.txt (one path per line, relative to CORE)
LIST="STATE/cleanup-move-list.txt"
if [ ! -f "$LIST" ]; then
  echo "Missing $LIST. Create it with relative paths to move into $TRASH."
  exit 2
fi

moved=0
while IFS= read -r p; do
  [ -z "$p" ] && continue
  case "$p" in
    .git/*|.git|*/.git/*) echo "SKIP (git internals): $p"; continue ;;
  esac
  if [ -e "$p" ]; then
    mkdir -p "$TRASH/$(dirname "$p")"
    mv -f "$p" "$TRASH/$p"
    echo "MOVED: $p -> $TRASH/$p"
    moved=$((moved+1))
  else
    echo "MISSING: $p"
  fi
done < "$LIST"

echo "{\"timestamp\":\"$TS\",\"trash\":\"$TRASH\",\"moved\":$moved}" > "STATE/cleanup-move-$TS.json"

git add TRASH "STATE/cleanup-move-$TS.json" "$LIST" 2>/dev/null || true
git commit -m "CLEAN: staged moves to TRASH ($TS)" >/dev/null 2>&1 || true
git push >/dev/null 2>&1 || true

echo "DONE: moved=$moved"
