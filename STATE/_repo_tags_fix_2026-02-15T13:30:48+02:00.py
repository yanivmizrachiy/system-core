import sys, json
from pathlib import Path
from datetime import datetime, timezone

src = Path(sys.argv[1])
out_json = Path(sys.argv[2])
out_md   = Path(sys.argv[3])
plan_dir = Path(sys.argv[4])

data = json.loads(src.read_text(encoding="utf-8"))

def parse_dt(s):
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

now = datetime.now(tz=timezone.utc)

rows = []
for r in data:
    name = (r.get("name") or "")
    url  = (r.get("url")  or "")
    vis  = "private" if r.get("isPrivate") else "public"
    upd0 = (r.get("updatedAt") or "")
    dt   = parse_dt(upd0)
    age_days = int((now - dt).total_seconds() // 86400) if dt else 10**9
    br = (((r.get("defaultBranchRef") or {}) or {}).get("name", "") or ""
    desc = (r.get("description") or "").replace("\n", " ").strip()

    if age_days <= 45:
        tag, why = "ACTIVE",  f"Updated {age_days}d ago"
    elif age_days <= 365:
        tag, why = "CLEANUP", f"Updated {age_days}d ago (review/sort, NO delete)"
    else:
        tag, why = "ARCHIVE", f"Updated {age_days}d ago (candidate archive)"

    rows.append({
        "name": name, "tag": tag, "why": why, "vis": vis,
        "updatedAt": upd0, "branch": br, "url": url, "desc": desc[:90]
    })

prio = {"ACTIVE": 0, "CLEANUP