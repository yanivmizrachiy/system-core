import sys, json, hashlib, base64, subprocess, datetime
from pathlib import Path
from datetime import timezone

def sh(args, check=True, capture=True, text=True):
    return subprocess.run(args, check=check, capture_output=capture, text=text)

def gh_api_json(path):
    # GH_TOKEN is provided by Actions env; gh will use it automatically
    r = sh(["gh", "api", "-H", "Accept: application/vnd.github+json", path], check=False)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "").strip() or f"gh api failed: {path}")
    try:
        return json.loads(r.stdout)
    except Exception as e:
        raise RuntimeError(f"bad json from gh api: {path}: {e}")

def safe_write(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def iso_now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8", errors="ignore")).hexdigest()

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def parse_iso(ts: str):
    try:
        # GitHub often returns ...Z
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.datetime.fromisoformat(ts)
    except Exception:
        return None

def days_since(dt):
    if not dt:
        return 10**9
    now = datetime.datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int((now - dt).total_seconds() / 86400)

def build_move_list_from_tree(owner, repo):
    """
    Build move-list without cloning:
    - fetch default branch tree recursively
    - mark typical build/cache/log artifacts
    """
    try:
        r = gh_api_json(f"repos/{owner}/{repo}")
        default_branch = r.get("default_branch") or "main"
    except Exception:
        default_branch = "main"

    # tree (recursive)
    tree = gh_api_json(f"repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1").get("tree", [])
    items = set()

    dir_names = {"node_modules","dist","build","out","output",".next",".cache",".parcel-cache",".turbo","coverage","__pycache__", ".pytest_cache"}
    file_ext = {".log",".tmp",".bak",".old",".swp",".swo"}
    file_names = {".DS_Store","Thumbs.db","npm-debug.log","yarn-error.log","pnpm-debug.log"}

    for entry in tree:
        p = entry.get("path") or ""
        t = entry.get("type")
        if not p or p.startswith(".git/"):
            continue
        parts = p.split("/")
        if "TRASH" in parts or "_TRASH" in parts:
            continue
        name = parts[-1]
        if t == "tree":
            if name in dir_names:
                items.add(p)
        elif t == "blob":
            if name in file_names:
                items.add(p)
            else:
                dot = name.rfind(".")
                suf = name[dot:].lower() if dot != -1 else ""
                if suf in file_ext:
                    items.add(p)
    return sorted(items)

def readme_sha256(owner, repo):
    """
    Best-effort: many repos have no README or are private with different perms.
    Return (sha256, ok_bool, error_str)
    """
    try:
        obj = gh_api_json(f"repos/{owner}/{repo}/readme")
        content_b64 = obj.get("content") or ""
        if not content_b64:
            return (None, False, "no_content")
        raw = base64.b64decode(content_b64.encode("utf-8", errors="ignore"))
        return (sha256_hex(raw), True, None)
    except Exception as e:
        return (None, False, str(e)[:220])

def main():
    if len(sys.argv) < 3:
        print("usage: governance_v4_auto.py <owner> <top_n>")
        sys.exit(2)

    owner = sys.argv[1].strip()
    try:
        top_n = int(sys.argv[2])
    except Exception:
        top_n = 20

    ts = iso_now()

    # Output dirs inside repo
    base = Path("STATE/governance-v4-auto") / ts
    out_json = base / "repo-intelligence-v4-auto.json"
    out_md   = base / "dashboard-v4-auto.md"
    out_err  = base / "errors.txt"
    out_ml_dir = base / "move-lists"
    out_dec_dir = Path("STATE/repo-decisions-auto") / ts

    errors = []

    # list repos
    # include private repos
    try:
        repos_raw = gh_api_json(f"users/{owner}/repos?per_page=200&sort=updated")
    except Exception as e:
        safe_write(out_err, f"FATAL: cannot list repos: {e}\n")
        raise

    repos = []
    for r in repos_raw:
        name = r.get("name")
        if not name:
            continue
        pushed = parse_iso(r.get("pushed_at") or r.get("updated_at") or "")
        age_days = days_since(pushed)
        desc = (r.get("description") or "").strip()
        private = bool(r.get("private"))
        url = r.get("html_url") or f"https://github.com/{owner}/{name}"

        risk = 0
        if age_days > 90: risk += 1
        if not desc: risk += 1

        repos.append({
            "name": name,
            "private": private,
            "url": url,
            "description": desc,
            "age_days": age_days,
            "risk": risk,
            "critical": "LOW" if (not private and age_days > 365) else ("HIGH" if (private and age_days <= 14) else "MEDIUM"),
        })

    # duplicates by name (case) and by description hash
    name_map = {}
    desc_map = {}
    for e in repos:
        lname = e["name"].lower()
        name_map.setdefault(lname, []).append(e["name"])
        if e["description"]:
            dh = md5_hex(e["description"])
            desc_map.setdefault(dh, []).append(e["name"])

    dup_names = [v for v in name_map.values() if len(v) > 1]
    dup_desc  = [v for v in desc_map.values() if len(v) > 1]
    dup_name_set = set(x for g in dup_names for x in g)
    dup_desc_set = set(x for g in dup_desc  for x in g)

    for e in repos:
        if e["name"] in dup_name_set: e["risk"] += 3
        if e["name"] in dup_desc_set: e["risk"] += 4

        if e["risk"] >= 6:
            e["category"] = "ARCHIVE_STRONG"
        elif e["risk"] >= 4:
            e["category"] = "DUPLICATE_RISK"
        elif e["risk"] >= 2:
            e["category"] = "REVIEW"
        else:
            e["category"] = "SAFE"

    repos.sort(key=lambda x: (-int(x.get("risk", 0)), -int(x.get("age_days", 0)), x.get("name", "").lower()))

    # README hash sampling topN (best-effort, non-fatal)
    sampled_ok = 0
    readme_hash_map = {}
    for e in repos[:max(0, top_n)]:
        h, ok, err = readme_sha256(owner, e["name"])
        e["readme_sha256"] = h
        e["readme_sampled"] = bool(ok)
        if ok and h:
            sampled_ok += 1
            readme_hash_map.setdefault(h, []).append(e["name"])
        elif err:
            errors.append({"repo": e["name"], "error": f"readme: {err}"})

    dup_readme = [v for v in readme_hash_map.values() if len(v) > 1]

    # Build move-lists (best-effort) for topN
    move_lists = []
    for e in repos[:max(0, top_n)]:
        try:
            items = build_move_list_from_tree(owner, e["name"])
            plan = out_ml_dir / f"{e[name]}__move-list.txt"
            safe_write(plan, "\n".join(items) + ("\n" if items else ""))
            e["move_list_count"] = len(items)
            e["move_list_path"] = str(plan)
            move_lists.append({"repo": e["name"], "count": len(items), "path": str(plan)})
        except Exception as ex:
            errors.append({"repo": e["name"], "error": f"move-list: {str(ex)[:220]}"})
            e["move_list_count"] = 0
            e["move_list_path"] = None

    # decisions (JSON) for topN
    for e in repos[:max(0, top_n)]:
        dec = out_dec_dir / f"{e[name]}.json"
        obj = {
            "repo": e["name"],
            "final_tag": ("ACTIVE" if e["age_days"] <= 45 else "ARCHIVE"),
            "move_list_count": int(e.get("move_list_count") or 0),
            "move_list_path": e.get("move_list_path"),
            "ts": ts,
            "policy": "NO DELETE. If we apply cleanup: MOVE ONLY to TRASH.",
        }
        safe_write(dec, json.dumps(obj, ensure_ascii=False, indent=2))

    out = {
        "generated": ts,
        "owner": owner,
        "total": len(repos),
        "top_n": top_n,
        "repos": repos,
        "duplicate_names": dup_names,
        "duplicate_descriptions": dup_desc,
        "duplicate_readme_sha256": dup_readme,
        "readme_sampled_ok": sampled_ok,
        "move_lists": move_lists,
        "errors": errors[:500],
        "policy": "NO DELETE (MOVE ONLY).",
    }
    safe_write(out_json, json.dumps(out, ensure_ascii=False, indent=2))

    # dashboard markdown
    counts = {}
    crit_counts = {}
    for e in repos:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
        crit_counts[e["critical"]] = crit_counts.get(e["critical"], 0) + 1

    dash = []
    dash.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    dash.append("")
    dash.append(f"Owner: {owner}")
    dash.append(f"Generated: {ts}")
    dash.append(f"Total repos: {len(repos)}")
    dash.append(f"README sampled (top {top_n}): {sampled_ok}")
    dash.append("")
    dash.append("## Category counts")
    for k in ["SAFE","REVIEW","DUPLICATE_RISK","ARCHIVE_STRONG"]:
        dash.append(f"- {k}: {counts.get(k,0)}")
    dash.append("")
    dash.append("## Critical counts")
    for k in ["HIGH","MEDIUM","LOW"]:
        dash.append(f"- {k}: {crit_counts.get(k,0)}")
    dash.append("")
    dash.append(f"## Highest risk (top {min(25,len(repos))})")
    for e in repos[:25]:
        vis = "private" if e.get("private") else "public"
        dash.append(f"- {e[name]} | risk={e[risk]} | {e[category]} | age={e[age_days]}d | {vis} | {e[url]}")
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
    dash.append("## Duplicate README (sha256) [sampled only]")
    if dup_readme:
        for g in dup_readme:
            dash.append("- " + ", ".join(g))
    else:
        dash.append("- none")
    dash.append("")
    dash.append("## Top move-lists (topN)")
    for m in sorted(move_lists, key=lambda x: -int(x.get("count",0)))[:25]:
        dash.append(f"- {m[repo]} | COUNT={m[count]} | {m[path]}")
    dash.append("")
    dash.append("## Errors (first 40)")
    if errors:
        for ee in errors[:40]:
            dash.append(f"- {ee.get(repo)} | {ee.get(error)}")
    else:
        dash.append("- none")

    safe_write(out_md, "\n".join(dash) + "\n")
    safe_write(out_err, "\n".join([f"{x.get(repo)}: {x.get(error)}" for x in errors]) + ("\n" if errors else ""))

    print("OK")

if __name__ == "__main__":
    main()
