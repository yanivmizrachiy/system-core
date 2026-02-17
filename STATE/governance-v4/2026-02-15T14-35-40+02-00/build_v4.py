import sys, json, subprocess, base64, hashlib
from pathlib import Path
from datetime import datetime, timezone

raw_path = Path(sys.argv[1])
out_json = Path(sys.argv[2])
out_md   = Path(sys.argv[3])
err_path = Path(sys.argv[4])
owner    = sys.argv[5]

def eprint(*a):
    err_path.write_text((err_path.read_text(encoding="utf-8") if err_path.exists() else "") + " ".join(map(str,a)) + "\n", encoding="utf-8")

def parse_dt(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z","+00:00"))
    except Exception:
        return None

def gh_api_json(endpoint):
    # endpoint like: repos/OWNER/REPO/readme
    try:
        out = subprocess.check_output(["gh","api",endpoint], stderr=subprocess.STDOUT).decode("utf-8","replace")
        return json.loads(out)
    except Exception as ex:
        eprint("gh_api_json fail:", endpoint, ex)
        return None

data = json.loads(raw_path.read_text(encoding="utf-8"))
now  = datetime.now(timezone.utc)

repos=[]
errors=[]

# base scoring (simple + stable)
name_map={}
desc_map={}
for r in data:
    name = (r.get("name") or "").strip()
    if not name:
        continue

    upd = parse_dt(r.get("updatedAt") or "")
    age = 999999 if not upd else int((now-upd).total_seconds()//86400)
    private = bool(r.get("isPrivate"))
    desc = (r.get("description") or "").replace("\n"," ").strip()
    url = r.get("url") or ""

    # critical heuristic (can evolve later)
    lname = name.lower()
    critical = "LOW"
    if ("system" in lname) or ("core" in lname):
        critical = "HIGH"
    elif age < 30:
        critical = "MEDIUM"

    risk = 0
    if private: risk += 1
    if age > 120: risk += 2
    elif age > 60: risk += 1
    if not desc: risk += 1

    name_map.setdefault(lname, []).append(name)
    if desc:
        dh = hashlib.md5(desc.encode("utf-8","ignore")).hexdigest()
        desc_map.setdefault(dh, []).append(name)

    repos.append({
        "name": name,
        "private": private,
        "age_days": age,
        "critical": critical,
        "risk": risk,
        "url": url,
        "updatedAt": (r.get("updatedAt") or ""),
        "description": desc[:180],
        "readme_sha256": None,
        "readme_sampled": False,
    })

dup_names=[v for v in name_map.values() if len(v)>1]
dup_desc=[v for v in desc_map.values() if len(v)>1]

dup_name_set=set(x for g in dup_names for x in g)
dup_desc_set=set(x for g in dup_desc for x in g)

for e in repos:
    if e["name"] in dup_name_set: e["risk"] += 3
    if e["name"] in dup_desc_set: e["risk"] += 2

# classify
for e in repos:
    if e["risk"] >= 6:
        e["category"]="ARCHIVE_STRONG"
    elif e["risk"] >= 4:
        e["category"]="DUPLICATE_RISK"
    elif e["risk"] >= 2:
        e["category"]="REVIEW"
    else:
        e["category"]="SAFE"

# sort: highest risk first, then oldest, then name
repos.sort(key=lambda x: (-int(x.get("risk",0)), -int(x.get("age_days",0)), x.get("name","").lower()))

# README sampling (top 20 only) to avoid rate limits
MAX_SAMPLE=20
sampled=0
for e in repos[:MAX_SAMPLE]:
    repo = e["name"]
    endpoint = f"repos/{owner}/{repo}/readme"
    j = gh_api_json(endpoint)
    if not j:
        errors.append({"repo": repo, "error": "readme_api_failed"})
        continue
    content_b64 = j.get("content")
    if not content_b64:
        errors.append({"repo": repo, "error": "readme_missing_content"})
        continue
    try:
        raw = base64.b64decode(content_b64.encode("utf-8"), validate=False)
        sha = hashlib.sha256(raw).hexdigest()
        e["readme_sha256"]=sha
        e["readme_sampled"]=True
        sampled += 1
    except Exception as ex:
        errors.append({"repo": repo, "error": f"readme_decode_failed: {ex}"})

# duplicates by README hash (within sampled only)
readme_map={}
for e in repos:
    if e.get("readme_sha256"):
        readme_map.setdefault(e["readme_sha256"], []).append(e["name"])
dup_readme=[v for v in readme_map.values() if len(v)>1]

out={
    "generated": now.isoformat(),
    "owner": owner,
    "total": len(repos),
    "sampled_readmes": sampled,
    "repos": repos,
    "duplicate_names": dup_names,
    "duplicate_descriptions": dup_desc,
    "duplicate_readme_sha256": dup_readme,
    "errors": errors,
}
out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# dashboard
cat_counts={}
crit_counts={}
for e in repos:
    cat_counts[e["category"]] = cat_counts.get(e["category"], 0) + 1
    crit_counts[e["critical"]] = crit_counts.get(e["critical"], 0) + 1

dash=[]
dash.append("# GOVERNANCE DASHBOARD v4 (OK)")
dash.append("")
dash.append(f"Owner: {owner}")
dash.append(f"Total repos: {len(repos)}")
dash.append(f"README sampled (top {MAX_SAMPLE} risk): {sampled}")
dash.append("")

dash.append("## Category counts")
for k in ["SAFE","REVIEW","DUPLICATE_RISK","ARCHIVE_STRONG"]:
    dash.append(f"- {k}: {cat_counts.get(k,0)}")
dash.append("")

dash.append("## Critical counts")
for k in ["HIGH","MEDIUM","LOW"]:
    dash.append(f"- {k}: {crit_counts.get(k,0)}")
dash.append("")

dash.append("## Highest risk (top 25)")
for e in repos[:25]:
    vis = "private" if e["private"] else "public"
    dash.append(f"- {e["name"]} | risk={e["risk"]} | {e["category"]} | age={e["age_days"]}d | {vis} | {e["url"]}")
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
    dash.append(f"- groups: {len(dup_desc)} (see JSON)")
else:
    dash.append("- none")
dash.append("")

dash.append("## Duplicate README (sha256, sampled only)")
if dup_readme:
    for g in dup_readme:
        dash.append("- " + ", ".join(g))
else:
    dash.append("- none")
dash.append("")

dash.append("## Build errors")
if errors:
    for ee in errors[:30]:
        dash.append(f"- {ee.get("repo")} | {ee.get("error")}")
else:
    dash.append("- none")

out_md.write_text("\n".join(dash) + "\n", encoding="utf-8")
