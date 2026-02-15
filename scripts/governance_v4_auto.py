#!/usr/bin/env python3
import os, sys, json, time, datetime, pathlib, urllib.request

ENGINE = "urllib_only_v4"

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def tok():
    return (os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_TOKEN")
            or os.environ.get("TOKEN")
            or "")

def api_get(url, token="", tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("X-GitHub-Api-Version", "2022-11-28")
            if token:
                req.add_header("Authorization", f"Bearer {token}")
            with urllib.request.urlopen(req, timeout=40) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return resp.status, dict(resp.headers), body
        except Exception as e:
            last = str(e)
            time.sleep(1 + i*2)
    raise RuntimeError(last or "unknown error")

def next_link(link_header):
    # Link: <...page=2>; rel="next", <...>; rel="last"
    if not link_header:
        return None
    parts = [p.strip() for p in link_header.split(",")]
    for p in parts:
        if rel=next in p:
            left = p.split(";")[0].strip()
            if left.startswith("<") and left.endswith(">"):
                return left[1:-1]
    return None

def list_repos_public(owner, token):
    # works for public repos; token not required
    repos = []
    url = f"https://api.github.com/users/{owner}/repos?per_page=100&type=owner"
    while url:
        st, hdr, body = api_get(url, token="")
        data = json.loads(body) if body else []
        if isinstance(data, list):
            repos.extend(data)
        url = next_link(hdr.get("Link",""))
    return repos

def list_repos_user(token):
    # requires token with appropriate access; returns private+public when allowed
    repos = []
    url = "https://api.github.com/user/repos?per_page=100&affiliation=owner"
    while url:
        st, hdr, body = api_get(url, token=token)
        data = json.loads(body) if body else []
        if isinstance(data, list):
            repos.extend(data)
        url = next_link(hdr.get("Link",""))
    return repos

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else ""
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    token = tok()
    ts_dir = now().replace(":", "-").replace("+", "_")
    out_dir = pathlib.Path("STATE/governance-v4") / ts_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    pub, usr = [], []
    pub_err, usr_err = "", ""

    try:
        pub = list_repos_public(owner, token="")
    except Exception as e:
        pub_err = str(e)[:300]

    if token:
        try:
            usr = list_repos_user(token)
        except Exception as e:
            usr_err = str(e)[:300]
    else:
        usr_err = "no_token_in_env"

    # merge by full_name or name
    seen = set()
    items = []
    for r in (usr + pub):
        key = r.get("full_name") or r.get("name") or ""
        if not key or key in seen:
            continue
        seen.add(key)
        items.append({
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
        })

    raw = {
        "generated": now(),
        "engine": ENGINE,
        "owner": owner,
        "token_present": bool(token),
        "public_count": len(pub),
        "userrepos_count": len(usr),
        "merged_total": len(items),
        "public_error": pub_err,
        "userrepos_error": usr_err,
    }
    (out_dir/"raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir/"repo-intelligence-v4.json").write_text(json.dumps({"generated": now(), "engine": ENGINE, "owner": owner, "total": len(items), "repos": items, "raw": raw}, ensure_ascii=False, indent=2), encoding="utf-8")

    dash = []
    dash.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    dash.append("")
    dash.append(f"engine: {ENGINE}")
    dash.append(f"Owner: {owner}")
    dash.append(f"Total repos: {len(items)}")
    dash.append("")
    dash.append("## Enumeration")
    dash.append(f"- token_present: {bool(token)}")
    dash.append(f"- public (/users/<owner>/repos): {len(pub)}" + ("" if not pub_err else f"  ERROR={pub_err}"))
    dash.append(f"- user (/user/repos): {len(usr)}" + ("" if not usr_err else f"  ERROR={usr_err}"))
    dash.append("")
    dash.append("## First repos")
    for x in items[:max(1, top_n)]:
        dash.append(f"- {x.get(\"name\") or \"?\"} | private={x.get(\"private\")}")
    (out_dir/"dashboard-v4.md").write_text("\n".join(dash) + "\n", encoding="utf-8")

    # RULES append
    rules = pathlib.Path("RULES.md")
    rules.touch(exist_ok=True)
    txt = rules.read_text(encoding="utf-8", errors="replace")
    mark = "### GOVERNANCE (AUTO)"
    if mark not in txt:
        txt += "\n\n" + mark + "\n- Runs recorded below.\n"
    txt += (
        f"\n- {now()} | PATCH: {ENGINE} enumeration (urllib only; no gh api)\n"
        f"  - totals: public={len(pub)} userrepos={len(usr)} merged={len(items)} token_present={bool(token)}\n"
        f"  - outputs: {out_dir}/dashboard-v4.md , {out_dir}/repo-intelligence-v4.json\n"
        f"  - policy: NO DELETE (MOVE ONLY)\n"
    )
    rules.write_text(txt, encoding="utf-8")
    print("OK")

if __name__ == "__main__":
    main()
