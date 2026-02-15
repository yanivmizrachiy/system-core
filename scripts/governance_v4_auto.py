#!/usr/bin/env python3
import os, sys, json, time, datetime, pathlib, urllib.request

ENGINE = "urllib_only_v4"

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def get_token():
    return (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("TOKEN") or "")

def api_get(url, tok="", tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("X-GitHub-Api-Version", "2022-11-28")
            if tok:
                req.add_header("Authorization", f"Bearer {tok}")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode("utf-8", errors="replace")
                return resp.status, dict(resp.headers), data
        except Exception as e:
            last = str(e)
            time.sleep(1 + i*2)
    raise RuntimeError(last or "unknown error")

def next_link(hdrs):
    link = (hdrs or {}).get("Link") or (hdrs or {}).get("link") or ""
    if not link:
        return None
    for part in [p.strip() for p in link.split(",")]:
        if rel=next in part:
            left = part.split(";")[0].strip()
            if left.startswith("<") and left.endswith(">"):
                return left[1:-1]
    return None

def list_repos_public(owner):
    url = f"https://api.github.com/users/{owner}/repos?per_page=100&type=owner&sort=pushed"
    out = []
    while url:
        st, hdrs, body = api_get(url, tok="")
        if st != 200:
            raise RuntimeError(f"public_status={st} body_head={body[:120]}")
        arr = json.loads(body) if body else []
        if not isinstance(arr, list):
            raise RuntimeError("public_not_list")
        out.extend(arr)
        url = next_link(hdrs)
    return out

def list_repos_user(tok):
    if not tok:
        return []
    url = "https://api.github.com/user/repos?per_page=100&affiliation=owner&sort=pushed"
    out = []
    while url:
        st, hdrs, body = api_get(url, tok=tok)
        if st != 200:
            raise RuntimeError(f"user_status={st} body_head={body[:120]}")
        arr = json.loads(body) if body else []
        if not isinstance(arr, list):
            raise RuntimeError("user_not_list")
        out.extend(arr)
        url = next_link(hdrs)
    return out

def normalize(r):
    return {
        "name": r.get("name",""),
        "full_name": r.get("full_name",""),
        "private": bool(r.get("private")),
        "archived": bool(r.get("archived")),
        "fork": bool(r.get("fork")),
        "default_branch": r.get("default_branch"),
        "pushed_at": r.get("pushed_at"),
        "updated_at": r.get("updated_at"),
        "open_issues": r.get("open_issues_count", 0),
        "size_kb": r.get("size", 0),
    }

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else (os.environ.get("OWNER") or "")
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("TOP_N") or "20")
    ts_dir = now_iso().replace(":","-")
    out_dir = pathlib.Path("STATE/governance-v4") / ts_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    tok = get_token()
    pub, user = [], []
    pub_err = ""
    user_err = ""

    try:
        pub = list_repos_public(owner) if owner else []
    except Exception as e:
        pub_err = str(e)[:500]

    try:
        user = list_repos_user(tok)
    except Exception as e:
        user_err = str(e)[:500]

    merged = {}
    for r in pub:
        nm = (r.get("name") or "")
        if nm:
            merged[nm] = normalize(r)
    for r in user:
        nm = (r.get("name") or "")
        if nm:
            merged[nm] = normalize(r)

    items = list(merged.values())
    items.sort(key=lambda x: (x.get("pushed_at") or x.get("updated_at") or ""), reverse=True)

    raw = {
        "generated": now_iso(),
        "engine": ENGINE,
        "owner": owner,
        "token_present": bool(tok),
        "public_count": len(pub),
        "userrepos_count": len(user),
        "merged_total": len(items),
        "public_error": pub_err,
        "userrepos_error": user_err,
    }

    (out_dir/"raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir/"repo-intelligence-v4.json").write_text(json.dumps({
        "generated": now_iso(),
        "engine": ENGINE,
        "owner": owner,
        "total": len(items),
        "repos": items
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    dash = []
    dash.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    dash.append("")
    dash.append(f"engine: {ENGINE}")
    dash.append(f"Owner: {owner}")
    dash.append(f"Total repos: {len(items)}")
    dash.append("")
    dash.append("## Enumeration")
    dash.append(f"- public (/users/<owner>/repos): {len(pub)}" + ("" if not pub_err else f"  ERROR={pub_err}"))
    dash.append(f"- user (/user/repos): {len(user)}" + ("" if not user_err else f"  ERROR={user_err}"))
    dash.append("")
    dash.append("## First repos")
    for x in items[:max(0, top_n)]:
        dash.append(f"- {x.get(name,?)} | private={x.get(private)} | archived={x.get(archived)} | fork={x.get(fork)}")
    (out_dir/"dashboard-v4.md").write_text("\n".join(dash) + "\n", encoding="utf-8")

    rules = pathlib.Path("RULES.md")
    rules.touch(exist_ok=True)
    txt = rules.read_text(encoding="utf-8", errors="replace")
    if "### GOVERNANCE (AUTO)" not in txt:
        txt += "\n\n### GOVERNANCE (AUTO)\n- Runs recorded below.\n"
    txt += (
        f"\n- {now_iso()} | PATCH: {ENGINE} (urllib-only, never-fail)\n"
        f"  - totals: public={len(pub)} userrepos={len(user)} merged={len(items)} token_present={bool(tok)}\n"
        f"  - policy: NO DELETE (MOVE ONLY)\n"
    )
    rules.write_text(txt, encoding="utf-8")

    print("OK")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        # never fail: still write something so Actions can commit
        try:
            out_dir = pathlib.Path("STATE/governance-v4") / (now_iso().replace(":","-") + "_FALLBACK")
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir/"raw.json").write_text(json.dumps({"generated": now_iso(), "engine": ENGINE, "fatal": str(e)[:800]}, ensure_ascii=False, indent=2), encoding="utf-8")
            (out_dir/"dashboard-v4.md").write_text("# GOVERNANCE DASHBOARD v4 (AUTO)\n\nengine: %s\nfatal: %s\n" % (ENGINE, str(e)[:800]), encoding="utf-8")
        except Exception:
            pass
        print("OK")
        raise SystemExit(0)
