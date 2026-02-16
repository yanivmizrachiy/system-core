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

<!-- AUTO:ACHIEVEMENTS:BEGIN -->
## ✅ הישגים מאומתים — 2026-02-16 (system-core)

**מצב נכון להיום:** Governance v4 רץ ב-GitHub Actions ומסיים `success` (ללא PAT), ומייצר תוצרים אמיתיים תחת `STATE/`.

### מה הצלחנו להשיג (מאומת)

- **Governance v4 יציב**:
  - ריצה מצליחה אחרונה שנבדקה: **workflow_run_id=22069147127** (status: completed | conclusion: success).
  - Commit רלוונטי אחרון שמייצג את המצב היציב: `ad77b97...` (כפי שנצפה בלוגים/HEAD).

- **הסרת תלות ב-PAT /user/repos**:
  - הזרימה עודכנה כך שלא תלויה ב־`/user/repos` (שדורש הרשאות שונות/מוגבלות), אלא עובדת בצורה שמתאימה ל-GITHUB_TOKEN.
  - המשמעות: GitHub Actions יכול לעבוד על **Public** ולפי ההרשאות הקיימות של הטוקן המובנה, בלי לדרוש סודות חיצוניים.

- **הקשחת api_get בקוד** (`scripts/governance_v4_auto.py`):
  - חתימה תקינה: `def api_get(url, tok, tries=3)`
  - טיפול ברור בשגיאות:
    - `401` → הודעה מפורשת על טוקן חסר/לא תקין.
    - `403` → עצירה מיידית עם הודעה (לא ריטריי) כדי לא להסתיר בעיית הרשאות/מדיניות.
    - `5xx` → ריטריי עם exponential backoff.
  - קומפילציה מקומית תקינה (`py_compile OK`) לפי בדיקות שבוצעו.

- **Workflow permissions מסודרות** (`.github/workflows/governance_v4_auto.yml`):
  - שימוש ב-`secrets.GITHUB_TOKEN`.
  - הרשאות מוגדרות ברמת workflow: `contents: write`, `actions: read`, `packages: read`.
  - Checkout + setup-python + run script + commit/push אם יש שינוי.

- **תיעוד עובד**:
  - `RULES.md` כבר כולל יומן עבודה ועקרונות: NO DELETE (MOVE ONLY), ותיוג “GitHub 2”.

### מה נכשל בעבר (לידע, כדי שלא נחזור על זה)

- ריצה קודמת נכשלה עם 403: **workflow_run_id=22063750978**, עם אבחנה שהייתה תלות ב-endpoint בעייתי/הרשאות.
- ההתקדמות בפועל: הצלחנו להפוך את הכשל הזה ל-**success** ולהחזיר את המערכת לירוק.

### מה כבר אפשר להשתמש בו *עכשיו* (שימושיות מיידית)

- להריץ Governance v4 בכל רגע ולקבל:
  - `STATE/governance-v4/<timestamp>/repo-intelligence-v4.json`
  - `STATE/governance-v4/<timestamp>/dashboard-v4.md`
- זה נותן לך תמונת מצב אמיתית של ריפואים (Top N), ומייצר Dashboard שמתחזק את עצמו דרך Actions.

### חסמים שנותרו (כדי שנדע מה עוד צריך)

- אם תרצה סריקה מלאה של כל הפרטיים בכל מצב/ארגון — ייתכן שנצטרך הרחבת הרשאות/מדיניות (אבל כרגע הזרימה עובדת ללא PAT עבור מה שמורשה).
- עדיין אין “טריגר תמיד-דלוק” (cron / issue listener) — כרגע ההפעלה היא ידנית/dispatch.

**עודכן אוטומטית:** 2026-02-16T20:53:01Z
<!-- AUTO:ACHIEVEMENTS:END -->


- 2026-02-16T20-56-06Z | governance_v4_auto.py (GITHUB_TOKEN only)
  - total_repos=57 top_n=20
  - outputs: STATE/governance-v4/2026-02-16T20-56-06Z/repo-intelligence-v4.json, STATE/governance-v4/2026-02-16T20-56-06Z/dashboard-v4.md

- 2026-02-16T20-59-44Z | governance_v4_auto.py (GITHUB_TOKEN only)
  - total_repos=57 top_n=20
  - outputs: STATE/governance-v4/2026-02-16T20-59-44Z/repo-intelligence-v4.json, STATE/governance-v4/2026-02-16T20-59-44Z/dashboard-v4.md
