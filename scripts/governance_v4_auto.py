#!/usr/bin/env python3
import os, sys, json, time, datetime, pathlib, urllib.request, urllib.parse

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def gh_token():
    return (os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_TOKEN")
            or os.environ.get("TOKEN")
            or "")

def api_get_json(url, token, tries=5):
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
                hdrs = dict(resp.headers)
                return json.loads(data), hdrs, resp.status
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
            lt = p.find("<")
            gt = p.find(">")
            if lt != -1 and gt != -1 and gt > lt:
                return p[lt+1:gt]
    return None

def paginate(url_first, token, errors, max_pages=100):
    out = []
    url = url_first
    pages = 0
    while url and pages < max_pages:
        data, hdrs, status = api_get_json(url, token)
        # GitHub sometimes returns dict {"message": "..."} on errors.
        if isinstance(data, dict):
            msg = data.get("message") or "API returned dict (error-like)"
            errors.append({"where":"paginate", "url": url.split("?")[0], "status": status, "message": msg[:300]})
            break
        if not isinstance(data, list):
            errors.append({"where":"paginate", "url": url.split("?")[0], "status": status, "message": f"unexpected type: {type(data).__name__}"})
            break
        out.extend(data)
        url = parse_next_link(hdrs.get("Link",""))
        pages += 1
        if len(data) == 0:
            break
    return out

def repo_tag(r):
    p = r.get("pushed_at") or r.get("updated_at") or ""
    if not p:
        return "UNKNOWN"
    try:
        dt = datetime.datetime.fromisoformat(p.replace("Z","+00:00"))
        age_days = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds()/86400.0
        return "ACTIVE" if age_days <= 45 else "ARCHIVE"
    except Exception:
        return "UNKNOWN"

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else ""
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    token = gh_token()

    ts_dir = now_iso().replace(":","-")
    out_dir = pathlib.Path("STATE/governance-v4") / ts_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    errors = []
    repos = []

    # 1) Prefer authenticated listing (private+public) if token exists and works
    if token:
        try:
            # quick auth check
            me, _, st = api_get_json("https://api.github.com/user", token)
            if isinstance(me, dict) and me.get("login"):
                # use /user/repos with pagination via Link
                url = "https://api.github.com/user/repos?" + urllib.parse.urlencode({
                    "affiliation":"owner",
                    "per_page":"100",
                    "sort":"pushed",
                    "direction":"desc"
                })
                repos = paginate(url, token, errors)
            else:
                errors.append({"where":"auth_check", "status": st, "message": str(me)[:200]})
        except Exception as e:
            errors.append({"where":"auth_check", "message": str(e)[:300]})

    # 2) Fallback: public repos via /users/{owner}/repos (works even if token is blocked)
    if not repos and owner:
        try:
            url = f"https://api.github.com/users/{owner}/repos?" + urllib.parse.urlencode({
                "per_page":"100",
                "sort":"pushed",
                "direction":"desc"
            })
            repos = paginate(url, token, errors)
        except Exception as e:
            errors.append({"where":"fallback_users_repos", "message": str(e)[:300]})

    items = []
    for r in repos:
        items.append({
            "name": r.get("name",""),
            "private": bool(r.get("private")),
            "archived": bool(r.get("archived")),
            "fork": bool(r.get("fork")),
            "default_branch": r.get("default_branch"),
            "pushed_at": r.get("pushed_at"),
            "updated_at": r.get("updated_at"),
            "open_issues": r.get("open_issues_count", 0),
            "size_kb": r.get("size", 0),
            "tag": repo_tag(r),
        })

    def risk_key(x):
        score = 0.0
        if not x["archived"]: score += 5
        if x["tag"] == "ACTIVE": score += 4
        score += min(int(x["open_issues"]), 50) / 10.0
        score += min(int(x["size_kb"]), 500000) / 100000.0
        if x["private"]: score += 0.5
        return -score

    highest = sorted(items, key=risk_key)[:top_n]

    out_json = out_dir / "repo-intelligence-v4.json"
    out_raw  = out_dir / "raw.json"
    out_md   = out_dir / "dashboard-v4.md"

    out_raw.write_text(json.dumps({
        "generated": now_iso(),
        "owner": owner,
        "token_present": bool(token),
        "repos_count": len(items),
        "errors": errors
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    out_json.write_text(json.dumps({
        "generated": now_iso(),
        "owner": owner,
        "total": len(items),
        "repos": items,
        "highest_risk": highest,
        "errors": errors
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    lines.append("")
    lines.append(f"Owner: {owner}")
    lines.append(f"Total repos: {len(items)}")
    lines.append("")
    if errors:
        lines.append("## Errors (during enumeration)")
        for e in errors[:12]:
            w = e.get("where","?")
            st = e.get("status","")
            msg = e.get("message","")
            lines.append(f"- {w} {st}: {msg}")
        lines.append("")
    lines.append("## Highest risk (top_n)")
    for x in highest:
        lines.append(f"- {x[name]} | tag={x[tag]} | private={x[private]} | archived={x[archived]} | issues={x[open_issues]} | size_kb={x[size_kb]}")
    lines.append("")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    rules = pathlib.Path("RULES.md"); rules.touch(exist_ok=True)
    mark = "### GOVERNANCE (AUTO)"
    txt = rules.read_text(encoding="utf-8", errors="replace")
    if mark not in txt:
        txt += "\n\n" + mark + "\n- Runs recorded below.\n"
    txt += (
        f"\n- {now_iso()} | PATCH: governance v4 enumeration hardened (auth+fallback+errors)\n"
        f"  - outputs: {out_json} , {out_md}\n"
        f"  - total_repos={len(items)} top_n={top_n} token_present={bool(token)}\n"
        f"  - policy: NO DELETE (MOVE ONLY to TRASH).\n"
    )
    rules.write_text(txt, encoding="utf-8")

    print("OK")

if __name__ == "__main__":
    main()
