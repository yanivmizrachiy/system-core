import json, sys
from datetime import datetime, timezone

raw_path, out_json, out_md, owner = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

data = json.loads(open(raw_path, "r", encoding="utf-8").read())
now = datetime.now(timezone.utc)

def parse_dt(s):
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def critical_of(name: str) -> str:
    n = (name or "").lower()
    # Explicit critical repos first (easy override)
    if n in ("system-core", "my-assistant", "termux", "pdf-system", "n8n"):
        return "HIGH"
    if "core" in n or "system" in n:
        return "HIGH"
    if "assistant" in n or "sync" in n or "automation" in n or "orchestr" in n:
        return "MEDIUM"
    return "LOW"

repos = []
for r in data:
    name = r.get("name") or ""
    upd = parse_dt(r.get("updatedAt") or "")
    age = 999999 if not upd else int((now - upd).total_seconds() // 86400)
    priv = bool(r.get("isPrivate"))
    desc = (r.get("description") or "").replace("\n", " ").strip()
    crit = critical_of(name)

    risk = 0
    risk += 3 if crit == "HIGH" else 2 if crit == "MEDIUM" else 0
    risk += 1 if priv else 0
    risk += 2 if age > 120 else 0
    risk += 2 if age > 365 else 0
    risk += 1 if not desc else 0

    repos.append({
        "name": name,
        "url": r.get("url") or "",
        "private": priv,
        "updatedAt": r.get("updatedAt") or "",
        "age_days": age,
        "critical": crit,
        "risk": risk,
        "desc": desc[:140]
    })

# Sort: highest risk first, then oldest, then name
repos_sorted = sorted(repos, key=lambda x: (-x["risk"], -x["age_days"], x["name"].lower()))

out = {
    "generated": now.isoformat(),
    "owner": owner,
    "total": len(repos_sorted),
    "policy": "NO DELETE. Governance is report-only. Any cleanup is MOVE-to-TRASH only.",
    "repos": repos_sorted,
}

with open(out_json, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
for rr in repos_sorted:
    c = rr.get("critical") or "LOW"
    counts[c] = counts.get(c, 0) + 1

dash = []
dash.append("# GOVERNANCE DASHBOARD v4")
dash.append("")
dash.append(f"Owner: {owner}")
dash.append(f"Total repos: {len(repos_sorted)}")
dash.append("")
dash.append("## Critical counts")
dash.append(f"- HIGH: {counts.get(HIGH,0)}")
dash.append(f"- MEDIUM: {counts.get(MEDIUM,0)}")
dash.append(f"- LOW: {counts.get(LOW,0)}")
dash.append("")
dash.append("## Highest risk (top 30)")
for rr in repos_sorted[:30]:
    vis = "private" if rr.get("private") else "public"
    dash.append(f"- {rr.get(name,)} | risk={rr.get(risk,0)} | {rr.get(critical,LOW)} | age={rr.get(age_days,?)}d | {vis} | {rr.get(url,)}")
dash.append("")
dash.append("## Archive candidates (>365d) (first 60)")
old = [rr for rr in repos_sorted if isinstance(rr.get(age_days), int) and rr[age_days] >= 365]
if not old:
    dash.append("- none")
else:
    for rr in old[:60]:
        vis = "private" if rr.get("private") else "public"
        dash.append(f"- {rr.get(name,)} | age={rr.get(age_days,?)}d | {vis} | {rr.get(url,)}")
dash.append("")
dash.append("## Next automation")
dash.append("- Optional: compute README hash only for top 20 risk to detect clones/duplicates safely (rate-limit aware).")

with open(out_md, "w", encoding="utf-8") as f:
    f.write("\n".join(dash) + "\n")

print("OK")
