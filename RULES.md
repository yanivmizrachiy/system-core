# כללים

## יומן עבודה (חובה להתעדכן אחרי כל פעולה)

### 2026-02-15
- דרישה/שינוי: Governance v4 הציג Total repos=0 למרות שיש ריפואים.
- בוצע בפועל: מעבר לספירה דרך endpoint מאומת /user/repos.
- בדיקה מקומית:
  - public_count = 53
  - accessible_count = 61
- מסקנה: הבעיה בהרשאות של GitHub Actions (לא בקוד המקומי).
- מדיניות: אין מחיקות — רק MOVE ל-TRASH.

## GOVERNANCE v4 (system-core)
- מנוע: scripts/governance_v4_auto.py (GitHub REST, ללא gh api).
- חובה: ב-Workflow env יש GITHUB_TOKEN, ואם רוצים private מלא — להגדיר Secret בשם GH_PAT עם הרשאות מתאימות.
- תוצר: STATE/governance-v4/** כולל dashboard-v4.md ו-raw.json.
- מדיניות: NO DELETE (MOVE ONLY ל-TRASH).

## GitHub 2 — שכבת אוטומציה (gpt2)

- ריפו ביצוע: yanivmizrachiy/github-2
- SSOT כללים: yanivmizrachiy/system-core/RULES.md (הפרק הזה)
- עקרונות על: NO DELETE (MOVE ONLY), תיעוד מלא, Commit רק כשיש שינוי
- בטיחות: executor חסום עד להגדרת Allowlist+Schema
- Governance: כל שינוי כאן ילווה בריצת governance_v4_auto

- GitHub2 bootstrap noted @ 2026-02-15T20:16:38+02:00

- 2026-02-15T18:17:31.891338 | APPLY MOVE-ONLY (Actions)
  - applied=0 scanned=5
  - policy: NO DELETE (MOVE ONLY to TRASH)


### GOVERNANCE (AUTO)
- Runs recorded below.

- 2026-02-16T15-46-20Z | governance_v4_auto.py (GITHUB_TOKEN only)
  - total_repos=54 top_n=20
  - outputs: STATE/governance-v4/2026-02-16T15-46-20Z/repo-intelligence-v4.json, STATE/governance-v4/2026-02-16T15-46-20Z/dashboard-v4.md
