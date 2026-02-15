#!/usr/bin/env python3
import os, sys, json, datetime, subprocess, pathlib

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def sh(cmd):
    return subprocess.check_output(cmd, text=True)

def gh_json_lines(args):
    # expects each line is valid JSON (one object)
    out = sh(args)
    items=[]
    for line in out.splitlines():
        line=line.strip()
        if not line: 
            continue
        try:
            items.append(json.loads(line))
        except:
            pass
    return items

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else ""
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    # 1) Public repos: always available (lists public repos)
    pub_err = None
    try:
        pub = gh_json_lines(["gh","api",f"/users/{owner}/repos","--paginate","-f","per_page=100","-f","type=owner","--jq",".[] | @json"])
    except Exception as e:
        pub = []
        pub_err = str(e)[:300]

    # 2) Private+public via /user/repos (depends on token scopes / fine-grained access)
    priv_err = None
    try:
        priv = gh_json_lines(["gh","api","/user/repos","--paginate","-f","per_page=100","-f","affiliation=owner","--jq",".[] | @json"])
    except Exception as e:
        priv = []
        priv_err = str(e)[:300]

    # Merge by name (priv wins if same)
    by_name = {}
    for r in pub:
        n = r.get("name")
        if n: by_name[n] = r
    for r in priv:
        n = r.get("name")
        if n: by_name[n] = r

    repos = list(by_name.values())

    items = []
    for r in repos:
        items.append({
            "name": r.get("name"),
            "private": bool(r.get("private")),
            "archived": bool(r.get("archived")),
            "pushed_at": r.get("pushed_at"),
            "size": int(r.get("size",0) or 0),
            "issues": int(r.get("open_issues_count",0) or 0),
        })

    ts = now().replace(":","-")
    out_dir = pathlib.Path("STATE/governance-v4") / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = {
        "generated": now(),
        "owner": owner,
        "public_count": len(pub),
        "userrepos_count": len(priv),
        "merged_total": len(items),
        "public_error": pub_err,
        "userrepos_error": priv_err,
    }
    (out_dir/"raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir/"repo-intelligence-v4.json").write_text(json.dumps({"generated":now(),"owner":owner,"total":len(items),"repos":items,"raw":raw}, ensure_ascii=False, indent=2), encoding="utf-8")

    dash=[]
    dash.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    dash.append("")
    dash.append("Owner: " + owner)
    dash.append("Total repos: " + str(len(items)))
    dash.append("")
    dash.append("## Enumeration")
    dash.append("- public (/users/{owner}/repos): " + str(len(pub)) + ("" if not pub_err else ("  ERROR=" + pub_err)))
    dash.append("- user (/user/repos): " + str(len(priv)) + ("" if not priv_err else ("  ERROR=" + priv_err)))
    dash.append("")
    dash.append("## First repos")
    for x in items[:top_n]:
        dash.append("- " + (x.get("name") or "?") + " | private=" + str(x.get("private")))
    (out_dir/"dashboard-v4.md").write_text("\n".join(dash) + "\n", encoding="utf-8")

    rules = pathlib.Path("RULES.md")
    rules.touch(exist_ok=True)
    with rules.open("a", encoding="utf-8") as f:
        f.write("\n- " + now() + " | PATCH: dual enumeration (public-first + optional /user/repos)\n")
        f.write("  - totals: public=" + str(len(pub)) + " userrepos=" + str(len(priv)) + " merged=" + str(len(items)) + "\n")
        f.write("  - policy: NO DELETE (MOVE ONLY)\n")

    print("OK")

if __name__ == "__main__":
    main()
