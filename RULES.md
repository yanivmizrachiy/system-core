# SYSTEM CORE – SINGLE SOURCE OF TRUTH

## 1. מטרת העל
לאחד את כל הפרויקטים, הסיכומים והריפואים למערכת אחת מסונכרנת, ללא כפילויות וללא סתירות.

## 2. ריפואים קיימים (מיפוי)
- math-materials-website
- sefer2
- termux
- my-assistant
- ahuzim
(יתעדכן אוטומטית עם כל ריפו חדש)

## 3. חוק ברזל
אחרי כל פעולה – חובה לעדכן RULES.md.
אין פעולה בלי תיעוד.
אין שינוי בלי חותמת זמן ISO.

## 4. קליטת סיכומים
כל סיכום חדש נכנס לתיקיית INBOX.
לאחר מיון – מועבר לקטגוריה מתאימה.
אסור למחוק סיכומים. רק לאחד.

## 5. מניעת סתירות
לפני כל הוספה:
- בדיקת כפילות
- בדיקת ניגוד מול סעיפים קיימים
- אם יש סתירה – נרשם Conflict Section

## 6. מצב מערכת
יעודכן בכל שינוי:
- מה בוצע
- מה פתוח
- חסמים
- אחוז התקדמות


---

## SYSTEM AUDIT – 2026-02-15T11:28:33+02:00

### פעולה שבוצעה
בוצע Full System Audit מקומי על:
- ריפואים מקומיים
- קבצי RULES
- Workflows
- קבצי status/state
- זיהוי שמות קבצים כפולים

### פלט נשמר ב:
STATE/full-audit-full-audit-2026-02-15_11-19-50.txt

### מטרה
מיפוי כפילויות וסיכונים מבניים לפני איחוד מערכת כולל.

### סטטוס
Audit בוצע.
שלב הבא: ניתוח ממצאים וניקוי כפילויות.

## Update 2026-02-15T11:28:33+02:00
- עודכן בעקבות פעולה חדשה


---

## CLEANUP ANALYSIS – 2026-02-15T11:34:08+02:00

בוצע ניתוח מבני מלא לזיהוי:
- קבצי Git פנימיים
- Hash objects גלויים
- כפילויות שמות
- Workflows כפולים
- קבצי state כפולים
- קבצי ביניים

פלט נשמר:
STATE/cleanup-plan-2026-02-15T11:34:08+02:00.md

סטטוס: ממתין לאישור מחיקה מבוקרת.

---

## CLASSIFICATION REPORT – 2026-02-15T11:34:52+02:00

בוצע סיווג מבני מלא של הקבצים:
- ליבה
- תיעוד
- סקריפטים
- קבצי רעש

פלט:
STATE/classification-2026-02-15T11:34:52+02:00.md

סטטוס: מוכן לשלב ארכוב ומחיקה מבוקרת.

---

## קטגוריה: SYSTEM

### שחזור יציב של core-log/core-status — 2026-02-15T11:41:16+02:00
[[CORE_LOG:2026-02-15|SYSTEM|שחזור יציב של core-log/core-status]]

**מה בוצע**
- נבנו מחדש הסקריפטים בלי heredoc/awk; נפתרה בעיית /SCRIPTS; נוצר snapshot

**מה הבא**
- להתחיל קליטת סיכומים לתוך INBOX + לקבוע ריפו יעד ל-remote של system-core

**חסמים**
- אין


---

## קטגוריה: SYSTEM

### סטטוס מערכת (snapshot) — 2026-02-15T11:41:16+02:00
[[CORE_LOG:2026-02-15|SYSTEM|סטטוס מערכת (snapshot)]]

**מה בוצע**
- נוצר STATE/status-2026-02-15T11:41:16+02:00.txt

**מה הבא**
- שלב הבא: INBOX + ניקוי כפילויות (רק move ל-TRASH)

**חסמים**
- אם אין remote ל-system-core: נחבר לריפו יעד


---

## קטגוריה: SYSTEM

### חיבור system-core ל-GitHub + push — 2026-02-15T11:42:42+02:00
[[CORE_LOG:2026-02-15|SYSTEM|חיבור system-core ל-GitHub + push]]

**מה בוצע**
- אומת ריפו מקומי; נוצר/אומת ריפו yanivmizrachiy/system-core; הוגדר origin; בוצע push ל-main

**מה הבא**
- להתחיל קליטת סיכומים ל-INBOX + להכין ניקוי כפילויות (move בלבד ל-TRASH)

**חסמים**
- אין


---

## קטגוריה: SYSTEM

### התקנת INBOX/INDEX/TRASH כלים — 2026-02-15T11:44:04+02:00
[[CORE_LOG:2026-02-15|SYSTEM|התקנת INBOX/INDEX/TRASH כלים]]

**מה בוצע**
- נוספו: inbox-add.sh, inbox-index.sh, trash-move.sh; נוצרו תיקיות INBOX/TRASH

**מה הבא**
- להתחיל לקלוט 3 סיכומים ראשונים ל-INBOX ואז לייצר index

**חסמים**
- אין


---

## קטגוריה: SYSTEM

### התקנת core-sync — 2026-02-15T11:44:39+02:00
[[CORE_LOG:2026-02-15|SYSTEM|התקנת core-sync]]

**מה בוצע**
- נוצר SCRIPTS/core-sync.sh (index+status+rules+push)

**מה הבא**
- להריץ core-sync אחרי כל פעולה משמעותית

**חסמים**
- אין


---

## חזון-על (לא משתנה)
- מערכת אחת מאוחדת שמנצלת את כל מה שכבר נבנה (Termux/GitHub/Workflows/Pages/Rules).\n- אין כפילויות ואין בלבול: SSOT אחד.\n- אוטומציה מקסימלית, ידני מינימלי.\n- אין מחיקה עיוורת: ניקוי רק באמצעות Move ל-TRASH + תיעוד.

---

## מטרות-על (רשימה מצטברת)
- איחוד ידע: קליטת סיכומים ל-INBOX ומיפוי לפי קטגוריות.\n- מיפוי ריפואים וקבצים קיימים והפחתת כפילויות.\n- חיזוק לולאות GitHub (Issue → Action → Commit → RAW/Pages) איפה שכבר קיימות.\n- דשבורד אחד שמציג סטטוס, ריצות אחרונות, חסמים.

---

## סטטוס חי (מתעדכן תמיד)
- מה בוצע לאחרונה: (ראה STATE/last_update.json)\n- מה פתוח עכשיו: \n- מה הבא בתור: \n- חסמים ידועים: \n- אחוז התקדמות: 

---

## תוכנית המשך (Roadmap קצר ומעשי)
1) קליטת סיכומים: 10 קבצים ראשונים ל-INBOX + index.\n2) מיפוי ריפואים/תיקיות: קישור לרשימת ריפואים קיימים + קישורים.\n3) ניקוי כפילויות: יצירת move-list שמרני → TRASH move → בדיקה.\n4) אינטגרציה: לחבר system-core כמטא-מרכז לכל ריפו קיים (בלי לשכפל פרויקטים).\n5) שדרוגים חכמים בלבד: רק מה שמשרת מטרות-על.

---

## קטגוריה: CLEANUP

### בוצע TRASH move אוטומטי (שמרני) — 2026-02-15T11:47:23+02:00
[[CORE_LOG:2026-02-15|CLEANUP|בוצע TRASH move אוטומטי (שמרני)]]

**מה בוצע**
- נוצר STATE/move-list-2026-02-15T11:47:23+02:00.txt; הועברו פריטים ל-TRASH/2026-02-15T11:47:23+02:00 (ללא מחיקה)

**מה הבא**
- להריץ core-sync + להתחיל קליטת סיכומים ל-INBOX (10 ראשונים)

**חסמים**
- אין


---

## קטגוריה: GITHUB

### מיפוי אוטומטי של כל הריפואים (inventory) — 2026-02-15T11:52:37+02:00
[[CORE_LOG:2026-02-15|GITHUB|מיפוי אוטומטי של כל הריפואים (inventory)]]

**מה בוצע**
- נוצרו: STATE/github-repos.json + STATE/github-repos.md; נמצאו 61 ריפואים בחשבון yanivmizrachiy

**מה הבא**
- השלב הבא: תיוג ריפואים (ACTIVE/ARCHIVE/CLEANUP) + תוכנית ניקוי כפילויות (MOVE ל-TRASH בלבד)

**חסמים**
- אין


---

## קטגוריה: GITHUB

### מיפוי ריפואים — רענון 2026-02-15T12:04:54+02:00 — 2026-02-15T12:04:56+02:00
[[CORE_LOG:2026-02-15|GITHUB|מיפוי ריפואים — רענון 2026-02-15T12:04:54+02:00]]

**מה בוצע**
- נוצרו: STATE/github-repos.json + STATE/github-repos.md; נמצאו 61 ריפואים בחשבון yanivmizrachiy

**מה הבא**
- השלב הבא: תיוג ACTIVE/ARCHIVE/CLEANUP (שמרני) + תוכנית ניקוי כפילויות לכל ריפו (MOVE בלבד ל-TRASH)

**חסמים**
- אין


---

## קטגוריה: GITHUB

### Inventory ריפואים — נבנה קובץ MD תקין — 2026-02-15T12:05:41+02:00
[[CORE_LOG:2026-02-15|GITHUB|Inventory ריפואים — נבנה קובץ MD תקין]]

**מה בוצע**
- נוצרו/עודכנו: STATE/github-repos.json + STATE/github-repos.md; נספרו 61 ריפואים

**מה הבא**
- השלב הבא: תיוג ריפואים (ACTIVE/ARCHIVE/CLEANUP) + יצירת תוכנית סדר וניקוי לכל ריפו (MOVE בלבד ל-TRASH)

**חסמים**
- אין


---

## קטגוריה: GITHUB

### Inventory ריפואים — build (argv-safe) 2026-02-15T12:07:25+02:00 — 2026-02-15T12:07:27+02:00
[[CORE_LOG:2026-02-15|GITHUB|Inventory ריפואים — build (argv-safe) 2026-02-15T12:07:25+02:00]]

**מה בוצע**
- נוצרו/עודכנו: STATE/github-repos.json + STATE/github-repos.md; נספרו 61 ריפואים

**מה הבא**
- הבא: תיוג ריפואים ACTIVE/ARCHIVE/CLEANUP + תכנית ניקוי שמרני לכל ריפו (MOVE בלבד ל-TRASH)

**חסמים**
- אין


---

## קטגוריה: GITHUB

### Inventory ריפואים — build (argv-safe) 2026-02-15T12:10:49+02:00 — 2026-02-15T12:10:52+02:00
[[CORE_LOG:2026-02-15|GITHUB|Inventory ריפואים — build (argv-safe) 2026-02-15T12:10:49+02:00]]

**מה בוצע**
- נוצרו/עודכנו: STATE/github-repos.json + STATE/github-repos.md; נספרו 61 ריפואים

**מה הבא**
- הבא: תיוג ריפואים ACTIVE/ARCHIVE/CLEANUP + תכנית ניקוי שמרני לכל ריפו (MOVE בלבד ל-TRASH)

**חסמים**
- אין


---

## קטגוריה: GITHUB

### Inventory ריפואים — build (argv-safe) 2026-02-15T12:11:11+02:00 — 2026-02-15T12:11:14+02:00
[[CORE_LOG:2026-02-15|GITHUB|Inventory ריפואים — build (argv-safe) 2026-02-15T12:11:11+02:00]]

**מה בוצע**
- נוצרו/עודכנו: STATE/github-repos.json + STATE/github-repos.md; נספרו 61 ריפואים

**מה הבא**
- הבא: תיוג ריפואים ACTIVE/ARCHIVE/CLEANUP + תכנית ניקוי שמרני לכל ריפו (MOVE בלבד ל-TRASH)

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### נוצרו תוכניות CLEANUP ראשוניות (FIX) — 1 ריפואים — 2026-02-15T12:53:42+02:00
[[CORE_LOG:2026-02-15|CLEANUP|נוצרו תוכניות CLEANUP ראשוניות (FIX) — 1 ריפואים]]

**מה בוצע**
- נוצר: STATE/cleanup-plans/2026-02-15T12:53:42+02:00 (תיקון NameError)

**מה הבא**
- הבא: לבחור ריפו ראשון ולהפיק לו move-list שמרני

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### אימות תוכניות CLEANUP (preview) — 2026-02-15T12:55:17+02:00
[[CORE_LOG:2026-02-15|CLEANUP|אימות תוכניות CLEANUP (preview)]]

**מה בוצע**
- נמצאה תיקייה: STATE/cleanup-plans/2026-02-15T12:53:42+02:00 ; קבצים: 1 ; בוצע preview (head) בטרמינל

**מה הבא**
- הבא: לבחור ריפו ראשון מתוך הקבצים ולהפיק לו move-list שמרני (MOVE ל-TRASH בלבד)

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### נוצר move-list שמרני לריפו: homerh-math-worksheets — 2026-02-15T12:57:05+02:00
[[CORE_LOG:2026-02-15|CLEANUP|נוצר move-list שמרני לריפו: homerh-math-worksheets]]

**מה בוצע**
- נוצר: /data/data/com.termux/files/home/system-core/STATE/cleanup-plans/2026-02-15T12:57:03+02:00/homerh-math-worksheets__move-list.txt ; מועמדים: 0 ; (ללא מחיקה, ללא הזזה עדיין)

**מה הבא**
- הבא: לבצע MOVE ל-TRASH רק אם הרשימה הגיונית (תריץ פקודת apply אחת שאשלח)

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### AUDIT שמרני לריפו: homerh-math-worksheets — 2026-02-15T12:58:32+02:00
[[CORE_LOG:2026-02-15|CLEANUP|AUDIT שמרני לריפו: homerh-math-worksheets]]

**מה בוצע**
- move-list שמרני יצא ריק (COUNT=0). נוצרו דוחות audit: /data/data/com.termux/files/home/system-core/STATE/repo-audits/2026-02-15T12:58:32+02:00

**מה הבא**
- הבא: להחליט TAG חדש לריפו (ACTIVE/ARCHIVE) לפי audit, ואז לעבור לריפו הבא מתיקיית cleanup-plans

**חסמים**
- אין


---

## קטגוריה: GITHUB

### החלטת TAG לריפו homerh-math-worksheets — 2026-02-15T13:00:41+02:00
[[CORE_LOG:2026-02-15|GITHUB|החלטת TAG לריפו homerh-math-worksheets]]

**מה בוצע**
- נמצא audit אחרון: /data/data/com.termux/files/home/system-core/STATE/repo-audits/2026-02-15T12:58:32+02:00; move-list היה ריק; נקבע TAG=ACTIVE; נשמר: /data/data/com.termux/files/home/system-core/STATE/repo-audits/2026-02-15T12:58:32+02:00/decision.txt

**מה הבא**
- הבא: לעבור לריפו הבא מתוך cleanup-plans ולהפיק move-list שמרני

**חסמים**
- אין


---

## קטגוריה: SYSTEM

### תיקון תקיעות pull (merge conflict) + ניקוי רעש ?? — 2026-02-15T13:16:57+02:00
[[CORE_LOG:2026-02-15|SYSTEM|תיקון תקיעות pull (merge conflict) + ניקוי רעש ??]]

**מה בוצע**
- בוצע merge --abort / reset --merge לפי הצורך; הוקשח .gitignore כדי להפסיק זיהום status בקבצי סביבה; בוצע commit+push

**מה הבא**
- להריץ core-sync ואז להמשיך לריפו הבא בתיקיית cleanup-plans

**חסמים**
- אין


---

## קטגוריה: SYSTEM

### תיקון תקיעות pull + הקשחת gitignore — 2026-02-15T13:17:19+02:00
[[CORE_LOG:2026-02-15|SYSTEM|תיקון תקיעות pull + הקשחת gitignore]]

**מה בוצע**
- אומת כניסה לריפו system-core; בוצע abort ל-merge תקוע (אם היה); עודכן .gitignore כדי להפסיק רעש; commit+push

**מה הבא**
- להמשיך לריפו הבא מתוך cleanup-plans (שמרני)

**חסמים**
- אין


---

## קטגוריה: SYSTEM

### system-core הוחזר לריפו עצמאי — 2026-02-15T13:20:27+02:00
[[CORE_LOG:2026-02-15|SYSTEM|system-core הוחזר לריפו עצמאי]]

**מה בוצע**
- אומת: TOP עכשיו צריך להיות system-core; main פעיל; origin=https://github.com/yanivmizrachiy/system-core.git; בוצע push

**מה הבא**
- להריץ core-sync ואז להמשיך CLEANUP לריפו הבא

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### טופל ריפו CLEANUP הבא: homerh-math-worksheets — 2026-02-15T13:25:59+02:00
[[CORE_LOG:2026-02-15|CLEANUP|טופל ריפו CLEANUP הבא: homerh-math-worksheets]]

**מה בוצע**
- נוצר move-list COUNT=0: /data/data/com.termux/files/home/system-core/STATE/repo-move-lists/2026-02-15T13:25:57+02:00/homerh-math-worksheets__move-list.txt ; נוצר AUDIT: STATE/repo-audits/2026-02-15T13:25:57+02:00/homerh-math-worksheets ; נקבע TAG=ACTIVE ונשמר: /data/data/com.termux/files/home/system-core/STATE/repo-decisions/homerh-math-worksheets.json

**מה הבא**
- הבא: לעבור לריפו CLEANUP הבא (תריץ שוב אותה פקודה)

**חסמים**
- אין


---

## קטגוריה: GITHUB

### Repo-tags refresh (FIX2) 2026-02-15T13:32:20+02:00 — 2026-02-15T13:32:21+02:00
[[CORE_LOG:2026-02-15|GITHUB|Repo-tags refresh (FIX2) 2026-02-15T13:32:20+02:00]]

**מה בוצע**
- נוצרו: STATE/repo-tags-2026-02-15T13:32:20+02:00.md + STATE/repo-tags-2026-02-15T13:32:20+02:00.json ; CLEANUP_COUNT=0 ; plans: STATE/cleanup-plans/2026-02-15T13:32:20+02:00

**מה הבא**
- הבא: להתחיל cycle לריפו הראשון בתיקיית plans

**חסמים**
- אין


---

## קטגוריה: GITHUB

### Repo-tags SMART refresh 2026-02-15T13:34:29+02:00 — 2026-02-15T13:34:29+02:00
[[CORE_LOG:2026-02-15|GITHUB|Repo-tags SMART refresh 2026-02-15T13:34:29+02:00]]

**מה בוצע**
- נוצרו: STATE/repo-tags-smart-2026-02-15T13:34:29+02:00.md + STATE/repo-tags-smart-2026-02-15T13:34:29+02:00.json ; CLEANUP_COUNT=41 ; plans: STATE/cleanup-plans/2026-02-15T13:34:29+02:00

**מה הבא**
- הבא: להתחיל cycle לריפו הראשון בתיקיית plans (move-list+audit+tag)

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### CLEANUP cycle: 14-1-26 — 2026-02-15T13:35:35+02:00
[[CORE_LOG:2026-02-15|CLEANUP|CLEANUP cycle: 14-1-26]]

**מה בוצע**
- move-list COUNT=0: /data/data/com.termux/files/home/system-core/STATE/repo-move-lists/2026-02-15T13:35:34+02:00/14-1-26__move-list.txt ; AUDIT: STATE/repo-audits/2026-02-15T13:35:34+02:00/14-1-26 ; TAG=ACTIVE ; DEC: /data/data/com.termux/files/home/system-core/STATE/repo-decisions/14-1-26.json

**מה הבא**
- הבא: להריץ שוב כדי לטפל בריפו הבא (או להפיק apply-move אם CNT>0)

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### CLEANUP DONE: 14-1-26 — 2026-02-15T13:37:32+02:00
[[CORE_LOG:2026-02-15|CLEANUP|CLEANUP DONE: 14-1-26]]

**מה בוצע**
- PLAN הועבר ל-DONE; decision_created=NO; TAG=ACTIVE; MOVE_LIST=STATE/repo-move-lists/2026-02-15T13:35:34+02:00/14-1-26__move-list.txt; AUDIT_DIR=STATE/repo-audits/2026-02-15T13:35:34+02:00/14-1-26; DEC=STATE/repo-decisions/14-1-26.json

**מה הבא**
- הבא: להריץ cycle על הריפו הבא ב-plans (אני אכוון)

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### סגירת DONE בפועל: 14-1-26 — 2026-02-15T13:38:56+02:00
[[CORE_LOG:2026-02-15|CLEANUP|סגירת DONE בפועל: 14-1-26]]

**מה בוצע**
- moved=NO (already moved or missing) ; from=STATE/cleanup-plans/2026-02-15T13:34:29+02:00 ; to=STATE/cleanup-plans-done/2026-02-15T13:34:29+02:00 ; next=-

**מה הבא**
- הבא: להריץ cycle על NEXT_REPO

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### CLEANUP cycle+DONE: ACHUZIM — 2026-02-15T13:40:03+02:00
[[CORE_LOG:2026-02-15|CLEANUP|CLEANUP cycle+DONE: ACHUZIM]]

**מה בוצע**
- TAG=ARCHIVE ; move-list COUNT=0 ; move-list=/data/data/com.termux/files/home/system-core/STATE/repo-move-lists/2026-02-15T13:40:02+02:00/ACHUZIM__move-list.txt ; audit=STATE/repo-audits/2026-02-15T13:40:02+02:00/ACHUZIM ; decision=/data/data/com.termux/files/home/system-core/STATE/repo-decisions/ACHUZIM.json ; plan->DONE=STATE/cleanup-plans-done/2026-02-15T13:34:29+02:00

**מה הבא**
- הבא: להריץ שוב כדי לטפל בריפו הבא

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### FIX sed error + rebuild move-list: ACHUZIM — 2026-02-15T13:41:56+02:00
[[CORE_LOG:2026-02-15|CLEANUP|FIX sed error + rebuild move-list: ACHUZIM]]

**מה בוצע**
- move-list rebuilt: COUNT=0 ; PLAN=STATE/repo-move-lists/2026-02-15T13:40:02+02:00/ACHUZIM__move-list.txt ; decision_updated=YES

**מה הבא**
- הבא: להריץ שוב את ה-cycle לריפו הבא בתיקיית plans

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### CYCLE+DONE: ahuzim — 2026-02-15T13:44:12+02:00
[[CORE_LOG:2026-02-15|CLEANUP|CYCLE+DONE: ahuzim]]

**מה בוצע**
- TAG=ACTIVE ; move-list COUNT=0 ; move-list=/data/data/com.termux/files/home/system-core/STATE/repo-move-lists/2026-02-15T13:44:11+02:00/ahuzim__move-list.txt ; audit=STATE/repo-audits/2026-02-15T13:44:11+02:00/ahuzim ; decision=/data/data/com.termux/files/home/system-core/STATE/repo-decisions/ahuzim.json ; plan->DONE=STATE/cleanup-plans-done/2026-02-15T13:34:29+02:00

**מה הבא**
- הבא: להריץ שוב כדי לטפל בריפו הבא

**חסמים**
- אין


---

## קטגוריה: CLEANUP

### CYCLE+DONE: ai-control-hub-test — 2026-02-15T13:47:05+02:00
[[CORE_LOG:2026-02-15|CLEANUP|CYCLE+DONE: ai-control-hub-test]]

**מה בוצע**
- TAG=ACTIVE ; move-list COUNT=0 ; move-list=STATE/repo-move-lists/2026-02-15T13:47:02+02:00/ai-control-hub-test__move-list.txt ; audit=STATE/repo-audits/2026-02-15T13:47:02+02:00/ai-control-hub-test ; decision=STATE/repo-decisions/ai-control-hub-test.json ; plan_moved=YES

**מה הבא**
- הבא: להמשיך לריפו הבא אוטומטית

**חסמים**
- אין


### GOVERNANCE (AUTO)
- Runs recorded below.

- 2026-02-15T14:28:43+02:00 | v3 recovery: dashboard rebuilt (hard-safe) | dir=STATE/governance-v3/2026-02-15T14:04:15+02:00
  - status: repo-intelligence.json ✅ ; dashboard.md ✅ ; stderr_file=STATE/governance-v3/2026-02-15T14:04:15+02:00/dashboard_build.stderr.txt
  - next: TURBO README-hash sampling (top-risk only, MAX=20) כדי לזהות כפילויות חכמות בלי RateLimit

- 2026-02-15T14:37:17+02:00 | v4 FAILED: dir=STATE/governance-v4/2026-02-15T14:35:40+02:00
  - outputs: OUT_JSON=STATE/governance-v4/2026-02-15T14:35:40+02:00/repo-intelligence-v4.json ; OUT_MD=STATE/governance-v4/2026-02-15T14:35:40+02:00/dashboard-v4.md
  - stderr: STATE/governance-v4/2026-02-15T14:35:40+02:00/py.stderr.txt

- 2026-02-15T14:45:20+02:00 | v4 OK: dir=STATE/governance-v4/2026-02-15T14:35:40+02:00
  - outputs: STATE/governance-v4/2026-02-15T14:35:40+02:00/repo-intelligence-v4.json , STATE/governance-v4/2026-02-15T14:35:40+02:00/dashboard-v4.md
  - note: README sampling may have partial failures; treated as non-fatal.
  - policy: NO DELETE (review/move-list only).
  - next: cleanup batch MAX=20 לפי top-risk מה-dashboard-v4.

- 2026-02-15T14:55:14+02:00 | cleanup-decision written (auto): repo=ai-control-hub-test
  - TAG=ACTIVE ; move-list COUNT=0 ; move-list=STATE/repo-move-lists/2026-02-15T13:47:02+02:00/ai-control-hub-test__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T14:55:14+02:00/ai-control-hub-test ; decision=STATE/repo-decisions/ai-control-hub-test.json
  - policy: NO DELETE (MOVE ONLY to TRASH when applying cleanup).

---

## קטגוריה: CLEANUP

### DECISION+AUGMENT (auto): ai-control-hub-test — 2026-02-15T14:55:17+02:00
[[CORE_LOG:2026-02-15|CLEANUP|DECISION+AUGMENT (auto): ai-control-hub-test]]

**מה בוצע**
- TAG=ACTIVE ; COUNT=0 ; move-list=STATE/repo-move-lists/2026-02-15T13:47:02+02:00/ai-control-hub-test__move-list.txt ; audit=STATE/repo-audits/2026-02-15T14:55:14+02:00/ai-control-hub-test ; decision=STATE/repo-decisions/ai-control-hub-test.json

**מה הבא**
- הבא: לבחור APPLY על בסיס decision/move-list

**חסמים**
- אין


- 2026-02-15T15:00:13+02:00 | cleanup-plan+decision (auto): repo=n8n
  - TAG=ACTIVE ; move-list COUNT=0 ; move-list=STATE/repo-move-lists/2026-02-15T15:00:13+02:00/n8n__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T15:00:13+02:00/n8n ; decision=STATE/repo-decisions/n8n.json
  - policy: NO DELETE (MOVE ONLY to TRASH when applying cleanup).

- 2026-02-15T15:00:13+02:00 | cleanup-plan+decision (auto): repo=pdf-system
  - TAG=ACTIVE ; move-list COUNT=9 ; move-list=STATE/repo-move-lists/2026-02-15T15:00:13+02:00/pdf-system__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T15:00:13+02:00/pdf-system ; decision=STATE/repo-decisions/pdf-system.json
  - policy: NO DELETE (MOVE ONLY to TRASH when applying cleanup).

- 2026-02-15T15:00:13+02:00 | cleanup-plan+decision (auto): repo=homerh-math-worksheets
  - TAG=ACTIVE ; move-list COUNT=0 ; move-list=STATE/repo-move-lists/2026-02-15T15:00:13+02:00/homerh-math-worksheets__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T15:00:13+02:00/homerh-math-worksheets ; decision=STATE/repo-decisions/homerh-math-worksheets.json
  - policy: NO DELETE (MOVE ONLY to TRASH when applying cleanup).

- 2026-02-15T15:00:13+02:00 | cleanup-plan+decision (auto): repo=14-1-26
  - TAG=ACTIVE ; move-list COUNT=0 ; move-list=STATE/repo-move-lists/2026-02-15T15:00:13+02:00/14-1-26__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T15:00:13+02:00/14-1-26 ; decision=STATE/repo-decisions/14-1-26.json
  - policy: NO DELETE (MOVE ONLY to TRASH when applying cleanup).

- 2026-02-15T15:00:13+02:00 | cleanup-plan+decision (auto): repo=assistant-control-mobile
  - TAG=ACTIVE ; move-list COUNT=0 ; move-list=STATE/repo-move-lists/2026-02-15T15:00:13+02:00/assistant-control-mobile__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T15:00:13+02:00/assistant-control-mobile ; decision=STATE/repo-decisions/assistant-control-mobile.json
  - policy: NO DELETE (MOVE ONLY to TRASH when applying cleanup).

- 2026-02-15T15:07:20+02:00 | NOOP-CLEAN (COUNT=0): repo=14-1-26
  - move-list=STATE/repo-move-lists/2026-02-15T15:00:13+02:00/14-1-26__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T15:00:13+02:00/14-1-26/noop_clean.txt
  - policy: NO DELETE (nothing to move).

- 2026-02-15T15:07:20+02:00 | NOOP-CLEAN (COUNT=0): repo=assistant-control-mobile
  - move-list=STATE/repo-move-lists/2026-02-15T15:00:13+02:00/assistant-control-mobile__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T15:00:13+02:00/assistant-control-mobile/noop_clean.txt
  - policy: NO DELETE (nothing to move).

- 2026-02-15T15:07:20+02:00 | NOOP-CLEAN (COUNT=0): repo=homerh-math-worksheets
  - move-list=STATE/repo-move-lists/2026-02-15T15:00:13+02:00/homerh-math-worksheets__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T15:00:13+02:00/homerh-math-worksheets/noop_clean.txt
  - policy: NO DELETE (nothing to move).

- 2026-02-15T15:07:20+02:00 | NOOP-CLEAN (COUNT=0): repo=n8n
  - move-list=STATE/repo-move-lists/2026-02-15T15:00:13+02:00/n8n__move-list.txt
  - audit=STATE/repo-audits/2026-02-15T15:00:13+02:00/n8n/noop_clean.txt
  - policy: NO DELETE (nothing to move).
