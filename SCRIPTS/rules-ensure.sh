#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
set +H 2>/dev/null || true
CORE="$HOME/system-core"
cd "$CORE"
touch RULES.md

ensure_block() {
  local marker="$1"
  local content="$2"
  if ! grep -Fq "$marker" RULES.md 2>/dev/null; then
    printf "\n---\n\n%s\n%s\n" "$marker" "$content" >> RULES.md
  fi
}

ensure_block "## חזון-על (לא משתנה)" \
"- מערכת אחת מאוחדת שמנצלת את כל מה שכבר נבנה (Termux/GitHub/Workflows/Pages/Rules).\n- אין כפילויות ואין בלבול: SSOT אחד.\n- אוטומציה מקסימלית, ידני מינימלי.\n- אין מחיקה עיוורת: ניקוי רק באמצעות Move ל-TRASH + תיעוד."

ensure_block "## מטרות-על (רשימה מצטברת)" \
"- איחוד ידע: קליטת סיכומים ל-INBOX ומיפוי לפי קטגוריות.\n- מיפוי ריפואים וקבצים קיימים והפחתת כפילויות.\n- חיזוק לולאות GitHub (Issue → Action → Commit → RAW/Pages) איפה שכבר קיימות.\n- דשבורד אחד שמציג סטטוס, ריצות אחרונות, חסמים."

ensure_block "## סטטוס חי (מתעדכן תמיד)" \
"- מה בוצע לאחרונה: (ראה STATE/last_update.json)\n- מה פתוח עכשיו: \n- מה הבא בתור: \n- חסמים ידועים: \n- אחוז התקדמות: "

ensure_block "## תוכנית המשך (Roadmap קצר ומעשי)" \
"1) קליטת סיכומים: 10 קבצים ראשונים ל-INBOX + index.\n2) מיפוי ריפואים/תיקיות: קישור לרשימת ריפואים קיימים + קישורים.\n3) ניקוי כפילויות: יצירת move-list שמרני → TRASH move → בדיקה.\n4) אינטגרציה: לחבר system-core כמטא-מרכז לכל ריפו קיים (בלי לשכפל פרויקטים).\n5) שדרוגים חכמים בלבד: רק מה שמשרת מטרות-על."

exit 0
