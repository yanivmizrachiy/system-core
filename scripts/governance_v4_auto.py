#!/usr/bin/env python3
import os, sys, json, datetime, subprocess, pathlib

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def run(cmd):
    return subprocess.check_output(cmd, text=True)

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else ""
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    # enumerate repos via gh api (stable + authenticated)
    try:
        raw = run(["gh","api","/user/repos","--paginate","--jq",".[]"])
        repos = []
        for line in raw.splitlines():
            try:
                repos.append(json.loads(line))
            except:
                pass
    except Exception as e:
        repos = []
        error = str(e)
    else:
        error = None

    items = []
    for r in repos:
        items.append({
            "name": r.get("name"),
            "private": r.get("private"),
            "archived": r.get("archived"),
            "pushed_at": r.get("pushed_at"),
            "size": r.get("size",0),
            "issues": r.get("open_issues_count",0)
        })

    ts = now().replace(":","-")
    out_dir = pathlib.Path("STATE/governance-v4") / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir/"repo-intelligence-v4.json").write_text(
        json.dumps({"generated":now(),"owner":owner,"total":len(items),"repos":items,"error":error},indent=2),
        encoding="utf-8"
    )

    dash = []
    dash.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    dash.append("")
    dash.append("Owner: " + str(owner))
    dash.append("Total repos: " + str(len(items)))
    dash.append("")
    if error:
        dash.append("## Error")
        dash.append(error)
        dash.append("")
    dash.append("## First repos")
    for x in items[:top_n]:
        dash.append("- " + x["name"])

    (out_dir/"dashboard-v4.md").write_text("\n".join(dash)+"\n",encoding="utf-8")

    rules = pathlib.Path("RULES.md")
    rules.touch(exist_ok=True)
    with rules.open("a",encoding="utf-8") as f:
        f.write("\n- "+now()+" | governance_v4_auto.py clean rebuild\n")
        f.write("  - total_repos="+str(len(items))+"\n")
        f.write("  - policy: NO DELETE (MOVE ONLY)\n")

    print("OK")

if __name__ == "__main__":
    main()
