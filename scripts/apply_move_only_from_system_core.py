import os, sys, json, subprocess, pathlib, datetime

def sh(*cmd, cwd=None):
    return subprocess.check_output(cmd, cwd=cwd).decode()

def move_only_trash(root, plan):
    moved=0
    missing=0
    for line in plan.read_text(encoding="utf-8").splitlines():
        rel=line.strip()
        if not rel: continue
        src=root/rel
        if src.exists():
            dst=root/"TRASH"/rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dst)
            moved+=1
        else:
            missing+=1
    return moved, missing

def main():
    owner=sys.argv[1]
    top_n=int(sys.argv[2])
    max_apply=int(sys.argv[3])
    ts=datetime.datetime.utcnow().isoformat()
    report=[]
    applied=0

    dash_dirs=sorted(pathlib.Path("STATE/governance-v4").glob("*"), reverse=True)
    if not dash_dirs: return
    dash=dash_dirs[0]

    plans=list(pathlib.Path("STATE/repo-move-lists").glob("*/**/*__move-list.txt"))
    plans=sorted(plans, reverse=True)[:top_n]

    for plan in plans:
        if applied>=max_apply: break
        repo=plan.name.replace("__move-list.txt","")
        root=pathlib.Path("/tmp")/repo
        subprocess.run(["rm","-rf",str(root)])
        try:
            sh("gh","repo","clone",f"{owner}/{repo}",str(root),"--","--depth","1")
        except:
            report.append({"repo":repo,"status":"CLONE_FAIL"})
            continue

        moved,missing=move_only_trash(root,plan)

        subprocess.run(["git","add","-A"],cwd=root)
        diff=sh("git","diff","--cached","--name-only",cwd=root)
        if diff.strip():
            subprocess.run(["git","config","user.name","yaniv-bot"],cwd=root)
            subprocess.run(["git","config","user.email","yaniv-bot@users.noreply.github.com"],cwd=root)
            subprocess.run(["git","commit","-m",f"cleanup: MOVE ONLY to TRASH ({ts})"],cwd=root)
            subprocess.run(["git","push"],cwd=root)
            report.append({"repo":repo,"status":"APPLIED","moved":moved})
            applied+=1
        else:
            report.append({"repo":repo,"status":"NO_CHANGES"})

    out=pathlib.Path("STATE/apply-reports")/ts
    out.mkdir(parents=True, exist_ok=True)
    (out/"apply_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")

    rules=pathlib.Path("RULES.md")
    rules.touch(exist_ok=True)
    with rules.open("a",encoding="utf-8") as f:
        f.write(f"\n- {ts} | APPLY MOVE-ONLY (Actions)\n")
        f.write(f"  - applied={applied} scanned={len(plans)}\n")
        f.write(f"  - policy: NO DELETE (MOVE ONLY to TRASH)\n")

if __name__=="__main__":
    main()
