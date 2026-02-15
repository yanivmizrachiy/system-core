#!/usr/bin/env python3
import os, sys, json, time, datetime, pathlib, urllib.request, urllib.parse

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def token():
    return (os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_TOKEN")
            or os.environ.get("TOKEN")
            or "")

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

def parse_next_link(link_hdr: str):
    if not link_hdr:
        return None
    parts = [p.strip() for p in link_hdr.split(",")]
    for p in parts:
        if rel=next in p:
            left = p.split(";")[0].strip()
            if left.startswith("<") and left.endswith(">"):
                return left[1:-1]
    return None

def paginate(url, tok="", hard_limit_pages=120):
    out = []
    page = 0
    while url and page < hard_limit_pages:
        status, hdrs, body = api_get(url, tok)
        if status != 200:
            raise RuntimeError(f"http={status} body={body[:200]}")
        try:
            chunk = json.loads(body)
        except Exception as e:
            raise RuntimeError(f"json_parse_fail: {e} body_head={body[:200]}")
        if not isinstance(chunk, list):
            raise RuntimeError(f"not_list: type={type(chunk)} body_head={body[:200]}")
        out.extend(chunk)
        url = parse_next_link(hdrs.get("Link",""))
        page += 1
    return out

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else ""
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    tok = token()

    ts = now().replace(":","-")
    out_dir = pathlib.Path("STATE/governance-v4") / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    pub_err = None
    user_err = None
    pub = []
    user = []

    # 1) Public (does not require token)
    try:
        u = f"https://api.github.com/users/{urllib.parse.quote(owner)}/repos?per_page=100&type=owner"
        pub = paginate(u, tok="")  # explicitly no token
    except Exception as e:
        pub_err = str(e)[:400]

    # 2) Owner repos via /user/repos (requires token; adds private if allowed)
    try:
        if tok:
            u = "https://api.github.com/user/repos?per_page=100&affiliation=owner"
            user = paginate(u, tok=tok)
        else:
            user_err = "no_token_present"
    except Exception as e:
        user_err = str(e)[:400]

    # merge by name
    by = {}
    for r in pub:
        n = r.get("name")
        if n: by[n] = r
    for r in user:
        n = r.get("name")
        if n: by[n] = r

    repos = list(by.values())
    items = [{
        "name": r.get("name"),
        "private": bool(r.get("private")),
        "archived": bool(r.get("archived")),
        "fork": bool(r.get("fork")),
        "default_branch": r.get("default_branch"),
        "pushed_at": r.get("pushed_at"),
        "updated_at": r.get("updated_at"),
        "open_issues": int(r.get("open_issues_count",0) or 0),
        "size_kb": int(r.get("size",0) or 0),
    } for r in repos]

    raw = {
        "generated": now(),
        "owner": owner,
        "token_present": bool(tok),
        "public_count": len(pub),
        "userrepos_count": len(user),
        "merged_total": len(items),
        "public_error": pub_err,
        "userrepos_error": user_err,
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
    dash.append("- public (/users/<owner>/repos): " + str(len(pub)) + ("" if not pub_err else ("  ERROR=" + pub_err)))
    dash.append("- user (/user/repos): " + str(len(user)) + ("" if not user_err else ("  ERROR=" + user_err)))
    dash.append("")
    dash.append("## First repos")
    for x in items[:top_n]:
        dash.append("- " + (x.get("name") or "?") + " | private=" + str(x.get("private")))
    (out_dir/"dashboard-v4.md").write_text("\n".join(dash) + "\n", encoding="utf-8")

    rules = pathlib.Path("RULES.md")
    rules.touch(exist_ok=True)
    txt = rules.read_text(encoding="utf-8", errors="replace")
    if "### GOVERNANCE (AUTO)" not in txt:
        txt += "\n\n### GOVERNANCE (AUTO)\n- Runs recorded below.\n"
    txt += ("\n- " + now() + " | PATCH: urllib enumeration (public-first + optional /user/repos)\n"
            "  - totals: public=" + str(len(pub)) + " userrepos=" + str(len(user)) + " merged=" + str(len(items)) + "\n"
            "  - policy: NO DELETE (MOVE ONLY)\n")
    rules.write_text(txt, encoding="utf-8")

    print("OK")

if __name__ == "__main__":
    main()
