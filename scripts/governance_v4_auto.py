#!/usr/bin/env python3
import os, json, time, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def api_get(url, tok="", tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("X-GitHub-Api-Version", "2022-11-28")
            if tok:
                req.add_header("Authorization", f"Bearer {tok}")
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read().decode("utf-8", errors="replace")
                return resp.status, dict(resp.headers), data
        except Exception as e:
            last = str(e)
            time.sleep(1 + i*2)
    raise RuntimeError(last or "unknown error")

def parse_next_link(link_hdr: str):
    # Link: <...>; rel="next", <...>; rel="last"
    if not link_hdr:
        return None
    parts = [p.strip() for p in link_hdr.split(",")]
    for p in parts:
        if rel_next in p:
            left = p.split(";")[0].strip()
            if left.startswith("<") and left.endswith(">"):
                return left[1:-1]
    return None

def list_repos(owner, tok):
    # Prefer authenticated /user/repos (includes private if token allows)
    # Fallback: public list /users/{owner}/repos
    errors = []
    merged = {}

    def harvest(url, label):
        nonlocal merged, errors
        next_url = url
        seen = 0
        while next_url:
            st, hdrs, body = api_get(next_url, tok=tok)
            if st != 200:
                errors.append({"where": label, "err": f"HTTP {st}"})
                break
            try:
                arr = json.loads(body)
            except Exception as e:
                errors.append({"where": label, "err": f"JSON parse error: {e}"})
                break
            if isinstance(arr, dict) and "message" in arr:
                errors.append({"where": label, "err": f"{arr.get(message)}"})
                break
            if not isinstance(arr, list):
                errors.append({"where": label, "err": f"unexpected payload type: {type(arr)}"})
                break
            for r in arr:
                name = r.get("name")
                if not name:
                    continue
                merged[name] = {
                    "name": name,
                    "private": bool(r.get("private", False)),
                    "archived": bool(r.get("archived", False)),
                    "open_issues": int(r.get("open_issues_count", 0) or 0),
                    "size_kb": int(r.get("size", 0) or 0),
                    "pushed_at": r.get("pushed_at") or "",
                    "default_branch": r.get("default_branch") or "main",
                    "html_url": r.get("html_url") or "",
                }
                seen += 1
            next_url = parse_next_link(hdrs.get("Link", ""))
        return seen

    # authenticated first
    c_user = 0
    c_pub  = 0

    if tok:
        c_user = harvest("https://api.github.com/user/repos?per_page=100&affiliation=owner", "user(/user/repos)")
    else:
        errors.append({"where": "token", "err": "no token provided; /user/repos skipped"})

    # public fallback (does not require token, but we still can send it)
    c_pub = harvest(f"https://api.github.com/users/{owner}/repos?per_page=100&type=owner", "public(/users/{owner}/repos)")

    return list(merged.values()), {"user_count": c_user, "public_count": c_pub, "errors": errors}

def main():
    owner = os.environ.get("OWNER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or ""
    if not owner:
        raise SystemExit("missing OWNER/GITHUB_REPOSITORY_OWNER")
    top_n = int(os.environ.get("TOP_N") or "20")

    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    repos, meta = list_repos(owner, tok)

    # tag heuristic
    def tag(r):
        return "ACTIVE" if (r.get("pushed_at") or "") else "UNKNOWN"

    items = []
    for r in repos:
        items.append({
            "name": r["name"],
            "private": r["private"],
            "archived": r["archived"],
            "open_issues": r["open_issues"],
            "size_kb": r["size_kb"],
            "tag": tag(r),
            "url": r["html_url"],
        })

    def risk_key(x):
        score = 0
        if not x["archived"]: score += 5
        if x["tag"] == "ACTIVE": score += 4
        score += min(int(x["open_issues"]), 50) / 10.0
        score += min(int(x["size_kb"]), 500000) / 100000.0
        if x["private"]: score += 0.5
        return -score

    highest = sorted(items, key=risk_key)[:top_n]

    out_dir = Path("STATE/governance-v4") / now_iso().replace(":", "-")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_raw  = out_dir / "raw.json"
    out_json = out_dir / "repo-intelligence-v4.json"
    out_md   = out_dir / "dashboard-v4.md"

    out_raw.write_text(json.dumps({
        "generated": now_iso(),
        "owner": owner,
        "token_present": bool(tok),
        "public_count": meta.get("public_count", 0),
        "userrepos_count": meta.get("user_count", 0),
        "merged_total": len(items),
        "errors": meta.get("errors", []),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    out_json.write_text(json.dumps({
        "generated": now_iso(),
        "owner": owner,
        "total": len(items),
        "repos": items,
        "highest_risk": highest,
        "errors": meta.get("errors", []),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# GOVERNANCE DASHBOARD v4 (AUTO)")
    lines.append("")
    lines.append(f"Owner: {owner}")
    lines.append(f"Total repos: {len(items)}")
    lines.append("")
    lines.append("## Enumeration")
    lines.append(f"- public (/users/{{owner}}/repos): {meta.get(public_count,0)}")
    lines.append(f"- user (/user/repos): {meta.get(user_count,0)} token_present={bool(tok)}")
    if meta.get("errors"):
        lines.append("")
        lines.append("## Errors")
        for e in meta["errors"][:10]:
            lines.append(f"- {e.get(where)}: {e.get(err)}")
    lines.append("")
    lines.append("## Highest risk (top_n)")
    for x in highest:
        lines.append(f"- {x[name]} | tag={x[tag]} | private={x[private]} | archived={x[archived]} | issues={x[open_issues]} | size_kb={x[size_kb]}")
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")

    # Append short run log into RULES.md
    rules = Path("RULES.md")
    rules.touch(exist_ok=True)
    mark = "### GOVERNANCE (AUTO)"
    txt = rules.read_text(encoding="utf-8", errors="replace")
    if mark not in txt:
        txt += "\n\n" + mark + "\n- Runs recorded below.\n"
    txt += (
        f"\n- {now_iso()} | governance_v4_auto.py (REST, no gh)\n"
        f"  - total_repos={len(items)} top_n={top_n} token_present={bool(tok)}\n"
        f"  - outputs: {out_json} , {out_md}\n"
        f"  - policy: NO DELETE (MOVE ONLY to TRASH).\n"
    )
    rules.write_text(txt, encoding="utf-8")

    print("OK")

if __name__ == "__main__":
    main()
