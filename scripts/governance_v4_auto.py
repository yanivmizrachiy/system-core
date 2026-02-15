#!/usr/bin/env python3
import os, sys, json, subprocess, hashlib, datetime, shutil, tempfile
from pathlib import Path
from datetime import timezone

def run(cmd, **kw):
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, **kw).decode("utf-8","replace")

def sh(cmd, **kw):
    p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw)
    return p.returncode, p.stdout.decode("utf-8","replace")

def gh_api_json(path):
    rc,out = sh(["gh","api",path])
    if rc!=0:
        return None, out.strip()
    try:
        return json.loads(out), ""
    except Exception as e:
        return None, f"json parse error: {e}"

def now_iso():
    return datetime.datetime.now().astimezone().isoformat()

def iso_utc_from_ts(ts):
    try:
        return datetime.datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
    except Exception:
        return ""

def safe_int(x, default=0):
    try: return int(x)
    except Exception: return default

DIR_NAMES = {"node_modules","dist","build","out","output",".next",".cache",".parcel-cache",".turbo","coverage","__pycache__", ".pytest_cache"}
FILE_EXT  = {".log",".tmp",".bak",".old",".swp",".swo"}
FILE_NAMES= {".DS_Store","Thumbs.db","npm-debug.log","yarn-error.log","pnpm-debug.log"}

def scan_move_list(repo_root: Path):
    items=set()
    for p in repo_root.rglob("*"):
        rel = p.relative_to(repo_root)
        if rel.parts and rel.parts[0]==".git":
            continue
        if "TRASH" in rel.parts or "_TRASH" in rel.parts:
            continue
        if p.is_dir():
            if p.name in DIR_NAMES:
                items.add(str(rel))
        else:
            if p.name in FILE_NAMES:
                items.add(str(rel))
            elif p.suffix.lower() in FILE_EXT:
                items.add(str(rel))
    return sorted(items)

def sha256_text(s: str):
    return hashlib.sha256(s.encode("utf-8","replace")).hexdigest()

def main():
    if len(sys.argv) < 3:
        print("usage: governance_v4_auto.py <owner> <top_n>", file=sys.stderr)
        sys.exit(2)
    owner = sys.argv[1]
    top_n = safe_int(sys.argv[2], 20)

    repo_root = Path.cwd()
    state_root = repo_root/"STATE"
    gov_dir = state_root/"governance-v4"/now_iso().replace(":","-")
    gov_dir.mkdir(parents=True, exist_ok=True)

    raw_path = gov_dir/"raw.json"
    out_json = gov_dir/"repo-intelligence-v4.json"
    out_md   = gov_dir/"dashboard-v4.md"

    errors=[]
    repos=[]

    # fetch repos list (paginated)
    page=1
    per=100
    all_items=[]
    while True:
        path=f"users/{owner}/repos?per_page={per}&page={page}&sort=updated"
        data, err = gh_api_json(path)
        if data is None:
            errors.append({"repo":"__LIST__", "error": f"gh api failed: {path} | {err}"})
            break
        all_items.extend(data)
        if len(data)<per:
            break
        page += 1

    raw_path.write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")

    # build basic intelligence
    now_ts = int(datetime.datetime.now(tz=timezone.utc).timestamp())
    for r in all_items:
        name = r.get("name","")
        private = bool(r.get("private", False))
        url = r.get("html_url","")
        pushed = r.get("pushed_at") or r.get("updated_at") or ""
        # compute age_days by pushed_at if possible
        age_days = 10**9
        try:
            if pushed:
                # pushed_at is ISO; parse roughly
                dt = datetime.datetime.fromisoformat(pushed.replace("Z","+00:00"))
                age_days = int((datetime.datetime.now(tz=timezone.utc)-dt).total_seconds()/86400)
        except Exception:
            pass

        # risk heuristics (simple + stable)
        risk = 0
        if private: risk += 1
        if age_days <= 14: risk += 1
        if not (r.get("has_issues", True)): risk += 1
        if (r.get("archived", False) or r.get("disabled", False)): risk += 2

        repos.append({
            "name": name,
            "private": private,
            "url": url,
            "age_days": age_days if age_days!=10**9 else 999999,
            "risk": risk,
            "category": "REVIEW" if risk>=2 else "SAFE",
            "critical": "HIGH" if risk>=4 else ("MEDIUM" if risk>=1 else "LOW"),
            "pushed_at": pushed,
        })

    repos.sort(key=lambda x: (-int(x.get("risk",0)), -int(x.get("age_days",0)), x.get("name","").lower()))

    # dashboard
    counts={}
    crit={}
    for e in repos:
        counts[e["category"]] = counts.get(e["category"],0)+1
        crit[e["critical"]]   = crit.get(e["critical"],0)+1

    dash=[]
    dash.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    dash.append("")
    dash.append(f"Owner: {owner}")
    dash.append(f"Total repos: {len(repos)}")
    dash.append("")
    dash.append("## Category counts")
    for k in ["SAFE","REVIEW"]:
        dash.append(f"- {k}: {counts.get(k,0)}")
    dash.append("")
    dash.append("## Critical counts")
    for k in ["HIGH","MEDIUM","LOW"]:
        dash.append(f"- {k}: {crit.get(k,0)}")
    dash.append("")
    dash.append("## Highest risk (top 25)")
    for e in repos[:25]:
        vis = "private" if e.get("private") else "public"
        dash.append(f"- {e[name]} | risk={e[risk]} | {e[category]} | age={e[age_days]}d | {vis} | {e[url]}")
    dash.append("")
    dash.append("## Notes")
    dash.append("- This is MOVE-ONLY governance. No delete is performed.")
    dash.append("")

    out_md.write_text("\n".join(dash)+"\n", encoding="utf-8")

    # === turbo: plans+decisions for top N (clone on runner/local) ===
    tsrun = now_iso()
    ml_dir = state_root/"repo-move-lists"/tsrun.replace(":","-")
    aud_root = state_root/"repo-audits"/tsrun.replace(":","-")
    dec_dir = state_root/"repo-decisions"
    apply_dir = state_root/"repo-apply-scripts"/tsrun.replace(":","-")
    ml_dir.mkdir(parents=True, exist_ok=True)
    aud_root.mkdir(parents=True, exist_ok=True)
    dec_dir.mkdir(parents=True, exist_ok=True)
    apply_dir.mkdir(parents=True, exist_ok=True)

    ok_count=0; fail_count=0; skip_count=0; clone_count=0
    top = [x["name"] for x in repos[:max(1, top_n)] if x.get("name")]
    for repo in top:
        dec_path = dec_dir/f"{repo}.json"
        if dec_path.exists() and dec_path.stat().st_size>0:
            skip_count += 1
            continue

        aud_dir = aud_root/repo
        aud_dir.mkdir(parents=True, exist_ok=True)

        # shallow clone into temp
        tmp = Path(tempfile.mkdtemp(prefix=f"repo_{repo}_"))
        rc,out = sh(["gh","repo","clone",f"{owner}/{repo}",str(tmp), "--", "--depth","1"])
        (aud_dir/"clone.log").write_text(out, encoding="utf-8")
        if rc!=0:
            (aud_dir/"clone_failed.txt").write_text("clone failed\n", encoding="utf-8")
            fail_count += 1
            shutil.rmtree(tmp, ignore_errors=True)
            continue
        clone_count += 1

        # git audit
        rc2, st = sh(["git","-C",str(tmp),"status","-sb"])
        (aud_dir/"git_status.txt").write_text(st, encoding="utf-8")
        rc3, lg = sh(["git","-C",str(tmp),"log","--oneline","-25"])
        (aud_dir/"git_log_last25.txt").write_text(lg, encoding="utf-8")
        rc4, rm = sh(["git","-C",str(tmp),"remote","-v"])
        (aud_dir/"git_remote.txt").write_text(rm, encoding="utf-8")

        # tag by last commit age
        tag="UNKNOWN"
        try:
            ct = run(["git","-C",str(tmp),"log","-1","--format=%ct"]).strip()
            ct_i = safe_int(ct, 0)
            age_days = (now_ts-ct_i)/86400 if ct_i else 10**9
            tag = "ACTIVE" if age_days<=45 else "ARCHIVE"
        except Exception:
            pass

        plan_path = ml_dir/f"{repo}__move-list.txt"
        items = scan_move_list(tmp)
        plan_path.write_text("\n".join(items)+("\n" if items else ""), encoding="utf-8")

        cnt=len(items)

        # decision json
        obj = {
            "repo": repo,
            "final_tag": tag,
            "move_list_count": cnt,
            "move_list_path": str(plan_path),
            "audit_dir": str(aud_dir),
            "ts": tsrun,
            "policy": "NO DELETE. If we apply cleanup: MOVE ONLY to TRASH.",
        }
        dec_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

        # apply script (MOVE ONLY) if non-empty
        if cnt>0:
            apply = apply_dir/f"{repo}__APPLY_MOVE_ONLY.sh"
            apply.write_text(
f"""#!/usr/bin/env bash
set -euo pipefail
ROOT="$HOME/{repo}"
PLAN="$HOME/system-core/{plan_path}"
[ -d "$ROOT/.git" ] || {{ echo "❌ missing clone: $ROOT"; exit 2; }}
[ -s "$PLAN" ] || {{ echo "❌ missing plan: $PLAN"; exit 3; }}
mkdir -p "$ROOT/TRASH"
n=0
while IFS= read -r rel; do
  [ -n "${{rel:-}}" ] || continue
  src="$ROOT/$rel"
  if [ -e "$src" ]; then
    dst="$ROOT/TRASH/$rel"
    mkdir -p "$(dirname "$dst")"
    mv -f "$src" "$dst"
    echo "MOVED: $rel"
    n=$((n+1))
  else
    echo "SKIP missing: $rel"
  fi
done < <(awk "NF" "$PLAN")
echo "✅ DONE moved=$n"
""", encoding="utf-8")
            os.chmod(apply, 0o755)

        shutil.rmtree(tmp, ignore_errors=True)
        ok_count += 1

    # Update RULES.md
    rules = repo_root/"RULES.md"
    rules.touch(exist_ok=True)
    mark="### GOVERNANCE (AUTO)"
    txt = rules.read_text(encoding="utf-8", errors="replace")
    if mark not in txt:
        txt += "\n\n" + mark + "\n- Runs recorded below.\n"
    txt += (
        f"\n- {tsrun} | governance_v4_auto.py finished\n"
        f"  - outputs: {out_json} , {out_md}\n"
        f"  - turbo: top_n={top_n} | decisions_written={ok_count} | clone_ok={clone_count} | fail={fail_count} | skip_existing={skip_count}\n"
        f"  - policy: NO DELETE (MOVE ONLY to TRASH when applying cleanup).\n"
        f"  - next: review dashboard-v4 + decisions; if you want apply -> run generated APPLY scripts (MOVE ONLY) OR automate apply via separate workflow.\n"
    )
    rules.write_text(txt, encoding="utf-8")

    # write intelligence json last (after turbo)
    out = {
        "generated": now_iso(),
        "owner": owner,
        "total": len(repos),
        "repos": repos,
        "errors": errors,
        "turbo": {
            "ts": tsrun,
            "top_n": top_n,
            "decisions_written": ok_count,
            "clone_ok": clone_count,
            "fail": fail_count,
            "skip_existing": skip_count,
            "move_lists_dir": str(ml_dir),
            "audits_dir": str(aud_root),
            "apply_dir": str(apply_dir),
        }
    }
    out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print("OK")

if __name__=="__main__":
    main()
