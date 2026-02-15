import sys, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

raw_path = Path(sys.argv[1])
out_json  = Path(sys.argv[2])
out_md    = Path(sys.argv[3])
err_path  = Path(sys.argv[4])
owner     = sys.argv[5]

def parse_dt(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None

def h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()

data = json.loads(raw_path.read_text(encoding="utf-8"))
now = datetime.now(timezone.utc)

name_map = {}
desc_map = {}
repos = []
errors = []

for r in data:
    try:
        name = (r.get("name") or "").strip()
        url  = (r.get("url") or "").strip()
        priv = bool(r.get("isPrivate"))
        upd0 = (r.get("updatedAt") or "").strip()
        desc = (r.get("description") or "").replace("\n", " ").strip()

        br = ""
        dbr = r.get("defaultBranchRef") or {}
        if isinstance(dbr, dict):
            br = (dbr.get("name") or "").strip()

        dt = parse_dt(upd0)
        age = 999999 if not dt else int((now - dt).total_seconds() // 86400)

        lname = name.lower()
        critical = "LOW"
        if ("system" in lname) or ("core" in lname):
            critical = "HIGH"
        elif age <= 30:
            critical = "MEDIUM"

        risk = 0
        if age > 120:
            risk += 2
        elif age > 45:
            risk += 1
        if not desc:
            risk += 1

        name_map.setdefault(lname, []).append(name)
        if desc:
            dh = h(desc)
            desc_map.setdefault(dh, []).append(name)

        repos.append({
            "name": name,
            "url": url,
            "private": priv,
            "updatedAt": upd0,
            "age_days": age,
            "branch": br,
            "critical": critical,
            "risk": risk,
            "desc": desc[:140],
        })

    except Exception as e:
        errors.append({"repo": str(r.get("name", "<unknown>")), "error": str(e)})

dup_names = [v for v in name_map.values() if len(v) > 1]
dup_desc  = [v for v in desc_map.values() if len(v) > 1]

dup_name_set = set(x for g in dup_names for x in g)
dup_desc_set = set(x for g in dup_desc for x in g)

for e in repos:
    if e["name"] in dup_name_set:
        e["risk"] += 3
    if e["name"] in dup_desc_set:
        e["risk"] += 4

    if e["risk"] >= 6:
        e["category"] = "ARCHIVE_STRONG"
    elif e["risk"] >= 4:
        e["category"] = "DUPLICATE_RISK"
    elif e["risk"] >= 2:
        e["category"] = "REVIEW"
    else:
        e["category"] = "SAFE"

repos.sort(key=lambda x: (-int(x.get("risk", 0)), -int(x.get("age_days", 0)), x.get("name", "").lower()))

out = {
    "generated": now.isoformat(),
    "owner": owner,
    "total": len(repos),
    "repos": repos,
    "duplicate_names": dup_names,
    "duplicate_descriptions": dup_desc,
    "errors": errors,
}

out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

counts = {}
crit_counts = {}
for e in repos:
    counts[e["category"]] = counts.get(e["category"], 0) + 1
    crit_counts[e["critical"]] = crit_counts.get(e["critical"], 0) + 1

dash = []
dash.append("# GOVERNANCE DASHBOARD v4")
dash.append("")
dash.append(f"Owner: {owner}")
dash.append(f"Total repos: {len(repos)}")
dash.append("")
dash.append("## Category counts")
for k in ["SAFE", "REVIEW", "DUPLICATE_RISK", "ARCHIVE_STRONG"]:
    dash.append(f"- {k}: {counts.get(k, 0)}")
dash.append("")
dash.append("## Critical counts")
for k in ["HIGH", "MEDIUM", "LOW"]:
    dash.append(f"- {k}: {crit_counts.get(k, 0)}")
dash.append("")
dash.append("## Highest risk (top 25)")
for e in repos[:25]:
    dash.append(f"- {e[name]} | risk={e[risk]} | {e[category]} | age={e[age_days]}d | {private if e[private] else public} | {e[url]}")
dash.append("")
dash.append("## Duplicate Names")
if dup_names:
    for g in dup_names:
        dash.append("- " + ", ".join(g))
else:
    dash.append("- none")
dash.append("")
dash.append("## Duplicate Descriptions (hash)")
if dup_desc:
    for g in dup_desc:
        dash.append("- " + ", ".join(g))
else:
    dash.append("- none")
dash.append("")
dash.append("## Build errors")
if errors:
    for e in errors[:30]:
        dash.append(f"- {e.get(repo)} | {e.get(error)}")
else:
    dash.append("- none")

out_md.write_text("\n".join(dash) + "\n", encoding="utf-8")
err_path.write_text("", encoding="utf-8")

print("OK")
