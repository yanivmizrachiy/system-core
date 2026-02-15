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
