#!/usr/bin/env bash
set -euo pipefail

OWNER="yanivmizrachiy"
DATE=$(date -Iseconds)
OUT="STATE/scan_${DATE}.md"

echo "# GOVERNANCE SCAN — ${DATE}" > "${OUT}"
echo "" >> "${OUT}"

REPOS=$(gh repo list ${OWNER} --limit 200 --json name -q ".[].name")

for r in ${REPOS}; do
  echo "## ${r}" >> "${OUT}"

  if gh api repos/${OWNER}/${r}/contents/RULES.md >/dev/null 2>&1; then
    echo "- RULES.md: OK" >> "${OUT}"
  else
    echo "- RULES.md: ❌ MISSING" >> "${OUT}"
  fi

  if gh api repos/${OWNER}/${r}/contents/README.md >/dev/null 2>&1; then
    echo "- README.md: OK" >> "${OUT}"
  else
    echo "- README.md: ❌ MISSING" >> "${OUT}"
  fi

  echo "" >> "${OUT}"
done

echo "Scan complete: ${OUT}"
