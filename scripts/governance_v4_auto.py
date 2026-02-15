#!/usr/bin/env python3
import os, sys, json, time, datetime, pathlib, urllib.request, urllib.parse

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def tok():
    return (os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_TOKEN")
            or os.environ.get("TOKEN")
            or "")

def api_get(url, token="", tries=5):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("X-GitHub-Api-Version", "2022-11-28")
            if token:
                req.add_header("Authorization", f"Bearer {token}")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode("utf-8", errors="replace")
                return resp.status, dict(resp.headers), data
        except Exception as e:
            last = str(e)
            time.sleep(1 + i*2)
    raise RuntimeError(last or "unknown error")

def next_link(link_hdr: str):
    # Link: <...page=2>; rel="next", <...page=4>; rel="last"
    if not link_hdr:
        return None
    parts = [p.strip() for p in link_hdr.split(",")]
    for p in parts:
        if rel=next in p:
            left = p.split(";")[0].strip()
            if left.startswith("<") and left.endswith(">"):
                return left[1:-1]
    return None

def paginate(url, token=""):
    out = []
    u = url
    while u:
        st, hdrs, body = api_get(u, token)
        if st != 200:
            raise RuntimeError(f"http={st}")
        j = json.loads(body)
        if isinstance(j, list):
            out.extend(j)
        else:
            # sometimes returns dict with message on auth issues
            raise RuntimeError(f"non-list json: {str(j)[:120]}")
        u = next_link(hdrs.get("Link") or hdrs.get("link") or "")
    return out

def uniq_by_fullname(items):
    m = {}
    for r in items:
        fn = r.get("full_name") or r.get("name") or ""
        if fn:
            m[fn] = r
    return list(m.values())

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("OWNER","")
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("TOP_N","20") or 20)

    token = tok()
    ts = now().replace(":", "-")
    out_dir = pathlib.Path("STATE/governance-v4") / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    pub = []
    usr = []
    pub_err = ""
    usr_err = ""

    # public list (works even without token for public repos, but rate-limited)
    try:
        pub_url = f"https://api.github.com/users/{owner}/repos?per_page=100&type=owner"
        pub = paginate(pub_url, token="")
    except Exception as e:
        pub_err = str(e)[:300]

    # user repos (needs token)
    if token:
        try:
            usr_url = "https://api.github.com/user/repos?per_page=100&affiliation=owner"
            usr = paginate(usr_url, token=token)
        except Exception as e:
            usr_err = str(e)[:300]
    else:
        usr_err = "NO_TOKEN"

    items = uniq_by_fullname(pub + usr)

    raw = {
        "generated": now(),
        "owner": owner,
        "token_present": bool(token),
        "public_count": len(pub),
        "userrepos_count": len(usr),
        "merged_total": len(items),
        "public_error": pub_err,
        "userrepos_error": usr_err,
    }

    (out_dir/"raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir/"repo-intelligence-v4.json").write_text(json.dumps({
        "generated": now(),
        "owner": owner,
        "total": len(items),
        "repos": [{
            "name": r.get("name"),
            "full_name": r.get("full_name"),
            "private": bool(r.get("private")),
            "archived": bool(r.get("archived")),
            "fork": bool(r.get("fork")),
            "default_branch": r.get("default_branch"),
            "pushed_at": r.get("pushed_at"),
            "updated_at": r.get("updated_at"),
            "open_issues": r.get("open_issues_count", 0),
            "size_kb": r.get("size", 0),
        } for r in items],
        "raw": raw
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    dash = []
    dash.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    dash.append("")
    dash.append("Owner: " + owner)
    dash.append("Total repos: " + str(len(items)))
    dash.append("")
    dash.append("## Enumeration")
    dash.append(f"- public (/users/<owner>/repos): {len(pub)}" + ("" if not pub_err else ("  ERROR=" + pub_err)))
    dash.append(f"- user (/user/repos): {len(usr)}" + ("" if not usr_err else ("  ERROR=" + usr_err)))
    dash.append("")
    dash.append("## First repos")
    for r in items[:top_n]:
        dash.append("- " + (r.get("full_name") or r.get("name") or "?") + " | private=" + str(bool(r.get("private"))))
    (out_dir/"dashboard-v4.md").write_text("\n".join(dash) + "\n", encoding="utf-8")

    # RULES append
    rules = pathlib.Path("RULES.md"); rules.touch(exist_ok=True)
    txt = rules.read_text(encoding="utf-8", errors="replace")
    if "### GOVERNANCE (AUTO)" not in txt:
        txt += "\n\n### GOVERNANCE (AUTO)\n- Runs recorded below.\n"
    txt += ("\n- " + now() + " | FIX: urllib-only repo enumeration (no gh api)\n"
            "  - outputs: " + str(out_dir/"repo-intelligence-v4.json") + " , " + str(out_dir/"dashboard-v4.md") + "\n"
            "  - totals: public=" + str(len(pub)) + " userrepos=" + str(len(usr)) + " merged=" + str(len(items)) + "\n"
            "  - policy: NO DELETE (MOVE ONLY)\n")
    rules.write_text(txt, encoding="utf-8")

    print("OK")

if __name__ == "__main__":
    main()
