#!/usr/bin/env python3
import os, sys, json, time, datetime, pathlib, urllib.request, urllib.parse

ENGINE = "urllib_only_never_fail_v1"

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def token():
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
    parts = [p.strip() for p in link.split(",")]
    for p in parts:
        if "rel=\"next\"" in p:
            left = p.split(";")[0].strip()
            if left.startswith("<") and left.endswith(">"):
                return left[1:-1]
    return None

def list_public(owner):
    # public enumeration does not require token
    url = f"https://api.github.com/users/{owner}/repos?per_page=100&type=owner"
    out = []
    while url:
        st, hdrs, body = api_get(url, tok="")
        if st != 200:
            raise RuntimeError(f"public_http_{st}: {body[:200]}")
        arr = json.loads(body)
        if not isinstance(arr, list):
            raise RuntimeError(f"public_not_list: {str(arr)[:200]}")
        out.extend(arr)
        url = next_link(hdrs)
    return out

def list_user_repos(tok):
    # needs token; returns private+public for the authenticated user
    url = "https://api.github.com/user/repos?per_page=100&affiliation=owner"
    out = []
    while url:
        st, hdrs, body = api_get(url, tok=tok)
        if st != 200:
            raise RuntimeError(f"user_http_{st}: {body[:200]}")
        arr = json.loads(body)
        if not isinstance(arr, list):
            raise RuntimeError(f"user_not_list: {str(arr)[:200]}")
        out.extend(arr)
        url = next_link(hdrs)
    return out

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else ""
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    ts = now().replace(":", "-")
    out_dir = pathlib.Path("STATE/governance-v4") / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    tok = token()
    pub, usr = [], []
    pub_err, usr_err = "", ""

    # NEVER FAIL: catch everything, always write outputs, exit 0
    try:
        try:
            pub = list_public(owner)
        except Exception as e:
            pub_err = str(e)[:500]

        if tok:
            try:
                usr = list_user_repos(tok)
            except Exception as e:
                usr_err = str(e)[:500]
        else:
            usr_err = "no_token_in_env"

        # merge unique by name
        by = {}
        for r in (pub + usr):
            name = r.get("name") or ""
            if name and name not in by:
                by[name] = {
                    "name": name,
                    "private": bool(r.get("private")),
                    "archived": bool(r.get("archived")),
                    "fork": bool(r.get("fork")),
                    "default_branch": r.get("default_branch"),
                    "pushed_at": r.get("pushed_at"),
                    "updated_at": r.get("updated_at"),
                    "size_kb": r.get("size", 0),
                    "open_issues": r.get("open_issues_count", 0),
                }
        items = list(by.values())

        raw = {
            "generated": now(),
            "engine": ENGINE,
            "owner": owner,
            "token_present": bool(tok),
            "public_count": len(pub),
            "userrepos_count": len(usr),
            "merged_total": len(items),
            "public_error": pub_err,
            "userrepos_error": usr_err,
        }
        (out_dir/"raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        (out_dir/"repo-intelligence-v4.json").write_text(json.dumps({"generated":now(),"engine":ENGINE,"owner":owner,"total":len(items),"repos":items,"raw":raw}, ensure_ascii=False, indent=2), encoding="utf-8")

        dash=[]
        dash.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
        dash.append("")
        dash.append(f"engine: {ENGINE}")
        dash.append(f"Owner: {owner}")
        dash.append(f"Total repos: {len(items)}")
        dash.append("")
        dash.append("## Enumeration")
        dash.append(f"- public (/users/<owner>/repos): {len(pub)}" + ("" if not pub_err else f"  ERROR={pub_err}"))
        dash.append(f"- user (/user/repos): {len(usr)}" + ("" if not usr_err else f"  ERROR={usr_err}"))
        dash.append("")
        dash.append("## First repos")
        for x in items[:top_n]:
            dash.append(f"- {x.get(\"name\")} | private={x.get(\"private\")}")
        (out_dir/"dashboard-v4.md").write_text("\n".join(dash) + "\n", encoding="utf-8")

        rules = pathlib.Path("RULES.md"); rules.touch(exist_ok=True)
        txt = rules.read_text(encoding="utf-8", errors="replace")
        if "### GOVERNANCE (AUTO)" not in txt:
            txt += "\n\n### GOVERNANCE (AUTO)\n- Runs recorded below.\n"
        txt += (f"\n- {now()} | governance_v4_auto.py ran ({ENGINE})\n"
                f"  - totals: public={len(pub)} userrepos={len(usr)} merged={len(items)} token_present={bool(tok)}\n"
                f"  - policy: NO DELETE (MOVE ONLY)\n")
        rules.write_text(txt, encoding="utf-8")

    except Exception as e:
        # absolute last resort: still write something
        (out_dir/"raw.json").write_text(json.dumps({"generated":now(),"engine":ENGINE,"owner":owner,"fatal":str(e)[:500]}, ensure_ascii=False, indent=2), encoding="utf-8")

    print("OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
