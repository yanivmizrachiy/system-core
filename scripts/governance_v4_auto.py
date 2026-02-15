#!/usr/bin/env python3
import os, sys, json, time, datetime, pathlib, urllib.request, urllib.parse

MARKER = "ENUM_ENGINE=urllib_only_v3"

def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def safe_ts():
    # filesystem-safe
    return now_utc().replace(":", "-")

def token():
    return (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "")

def api_get(url, tok="", tries=5):
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

def fetch_all(url, tok=""):
    items = []
    err = ""
    try:
        while url:
            st, hdrs, body = api_get(url, tok=tok)
            if st != 200:
                err = f"HTTP_{st}"
                break
            data = json.loads(body)
            if not isinstance(data, list):
                err = "NON_LIST_RESPONSE"
                break
            items.extend(data)
            url = parse_next_link(hdrs.get("Link",""))
    except Exception as e:
        err = str(e)
    return items, err

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else ""
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    tok = token()

    out_dir = pathlib.Path("STATE/governance-v4") / safe_ts()
    out_dir.mkdir(parents=True, exist_ok=True)

    # public list (works even without token, but only public repos)
    pub_url = f"https://api.github.com/users/{owner}/repos?per_page=100&type=owner"
    pub, pub_err = fetch_all(pub_url, tok="")

    # private+public via /user/repos (requires token with proper access)
    user_url = "https://api.github.com/user/repos?per_page=100&affiliation=owner"
    user, user_err = fetch_all(user_url, tok=tok) if tok else ([], "NO_TOKEN")

    # merge by name
    seen = {}
    for r in pub + user:
        name = (r.get("name") or "").strip()
        if not name:
            continue
        seen[name] = r
    items = list(seen.values())

    raw = {
        "generated": now_utc(),
        "owner": owner,
        "marker": MARKER,
        "token_present": bool(tok),
        "public_count": len(pub),
        "userrepos_count": len(user),
        "merged_total": len(items),
        "public_error": pub_err,
        "userrepos_error": user_err,
    }
    (out_dir/"raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir/"repo-intelligence-v4.json").write_text(json.dumps({"generated":now_utc(),"owner":owner,"total":len(items),"repos":[{"name":x.get("name"),"private":x.get("private"),"archived":x.get("archived"),"updated_at":x.get("updated_at"),"pushed_at":x.get("pushed_at")} for x in items], "raw": raw}, ensure_ascii=False, indent=2), encoding="utf-8")

    dash = []
    dash.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    dash.append("")
    dash.append(f"Owner: {owner}")
    dash.append(f"Total repos: {len(items)}")
    dash.append("")
    dash.append(f"{MARKER}")
    dash.append("")
    dash.append("## Enumeration")
    dash.append(f"- public (/users/<owner>/repos): {len(pub)}" + ("" if not pub_err else f"  ERROR={pub_err}"))
    dash.append(f"- user (/user/repos): {len(user)}" + ("" if not user_err else f"  ERROR={user_err}"))
    dash.append("")
    dash.append("## First repos")
    for x in sorted(items, key=lambda r: (r.get("name") or ""))[:top_n]:
        dash.append(f"- {(x.get(name) or ?)} | private={bool(x.get(private))}")
    (out_dir/"dashboard-v4.md").write_text("\n".join(dash) + "\n", encoding="utf-8")

    rules = pathlib.Path("RULES.md"); rules.touch(exist_ok=True)
    txt = rules.read_text(encoding="utf-8", errors="replace")
    if "### GOVERNANCE (AUTO)" not in txt:
        txt += "\n\n### GOVERNANCE (AUTO)\n- Runs recorded below.\n"
    txt += (
        f"\n- {now_utc()} | PATCH: {MARKER}\n"
        f"  - totals: public={len(pub)} userrepos={len(user)} merged={len(items)} token_present={bool(tok)}\n"
        f"  - outputs: {out_dir}/dashboard-v4.md , {out_dir}/raw.json\n"
        f"  - policy: NO DELETE (MOVE ONLY)\n"
    )
    rules.write_text(txt, encoding="utf-8")

    print("OK")

if __name__ == "__main__":
    main()
