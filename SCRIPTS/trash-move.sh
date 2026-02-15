#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
CORE="$HOME/system-core"
cd "$CORE"
[ $# -ge 1 ] || { echo "Usage: trash-move <path1> [path2...]"; exit 2; }
TS="$(date -Iseconds)"
DST="TRASH/$TS"
mkdir -p "$DST"
for p in "$@"; do
  [ -e "$p" ] || { echo "SKIP (missing): $p"; continue; }
  mv -n "$p" "$DST/" || true
  echo "MOVED: $p -> $DST/"
done
echo "$DST"
