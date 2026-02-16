#!/usr/bin/env python3
import os, json, time, urllib.request, urllib.parse, urllib.error, sys
from datetime import datetime, timezone
from pathlib import Path

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

def api_get(url, tok, tries=3):
    """Production-grade API call with exponential backoff - GITHUB_TOKEN only."""
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
        
        except urllib.error.HTTPError as e:
            status = e.code
            if status == 401:
                raise RuntimeError("HTTP 401: Token invalid. Ensure GITHUB_TOKEN is set.")
            elif status == 403:
                # Do NOT retry 403 - it won't succeed
                raise RuntimeError(f"HTTP 403: Forbidden. Check API rate limits.")
            elif status >= 500:
                if i < tries - 1:
                    wait_time = 2 ** i
                    print(f"HTTP {status}: Server error. Retry in {wait_time}s...", file=sys.stderr)
                    time.sleep(wait_time)
                    continue
                else:
                    raise RuntimeError(f"HTTP {status}: Server error after {tries} attempts.")
            else:
                raise RuntimeError(f"HTTP {status}: {e.reason}")
        
        except urllib.error.URLError as e:
            if i < tries - 1:
                wait_time = 2 ** i
                print(f"Network error: {e.reason}. Retry in {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
                continue
            else:
                raise RuntimeError(f"Network error after {tries} attempts: {e.reason}")
        
        except Exception as e:
            if i < tries - 1:
                wait_time = 2 ** i
                print(f"Unexpected error: {e}. Retry in {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
                continue
            else:
                raise RuntimeError(f"Unknown error after {tries} attempts: {e}")
    
    raise RuntimeError("Retry exhausted")

def parse_next_link(link_hdr: str):
    if not link_hdr:
        return None
    parts = [p.strip() for p in link_hdr.split(",")]
    for p in parts:
        if 'rel="next"' in p:
            left = p.split(";")[0].strip()
            if left.startswith("<") and left.endswith(">"):
                return left[1:-1]
    return None

def list_repos(owner, tok):
    """List repos using ONLY /users/{owner}/repos - no /user/repos dependency."""
    repos = {}
    next_url = f"https://api.github.com/users/{owner}/repos?type=owner&per_page=100"
    seen = 0
    
    while next_url:
        st, hdrs, body = api_get(next_url, tok)
        if st != 200:
            raise RuntimeError(f"HTTP {st} from /users/{owner}/repos")
        
        try:
            arr = json.loads(body)
        except Exception as e:
            raise RuntimeError(f"JSON parse error: {e}")
        
        if isinstance(arr, dict) and "message" in arr:
            raise RuntimeError(f"API error: {arr.get('message')}")
        
        if not isinstance(arr, list):
            raise RuntimeError(f"Unexpected payload type: {type(arr)}")
        
        for r in arr:
            name = r.get("name")
            if not name:
                continue
            repos[name] = {
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
    
    return list(repos.values()), {"count": seen}

def main():
    # Authentication guard
    tok = (os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()
    
    if not tok:
        print("ERROR: GITHUB_TOKEN not found.", file=sys.stderr)
        sys.exit(1)
    
    # Self-test mode
    if "--self-test" in sys.argv:
        print("[SELF-TEST MODE]")
        print(f"Token present: {bool(tok)}")
        
        owner = os.environ.get("GITHUB_REPOSITORY_OWNER") or "yanivmizrachiy"
        try:
            repos, meta = list_repos(owner, tok)
            print(f"Owner: {owner}")
            print(f"Repos found: {len(repos)}")
            print("Self-test PASSED")
            sys.exit(0)
        except Exception as e:
            print(f"Self-test FAILED: {e}", file=sys.stderr)
            sys.exit(1)
    
    owner = os.environ.get("OWNER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or ""
    if not owner:
        raise SystemExit("missing OWNER/GITHUB_REPOSITORY_OWNER")
    
    top_n = int(os.environ.get("TOP_N") or "20")
    
    repos, meta = list_repos(owner, tok)
    
    def tag(r):
        return "ACTIVE" if r.get("pushed_at") else "UNKNOWN"
    
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
    
    out_dir = Path("STATE/governance-v4") / now_iso()
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_raw = out_dir / "raw.json"
    out_json = out_dir / "repo-intelligence-v4.json"
    out_md = out_dir / "dashboard-v4.md"
    
    out_raw.write_text(json.dumps({
        "generated": now_iso(),
        "owner": owner,
        "token_present": bool(tok),
        "repo_count": len(items),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    
    out_json.write_text(json.dumps({
        "generated": now_iso(),
        "owner": owner,
        "total": len(items),
        "repos": items,
        "highest_risk": highest,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    
    lines = [
        "# GOVERNANCE DASHBOARD v4 (AUTO)",
        "",
        f"Owner: {owner}",
        f"Total repos: {len(items)}",
        "",
        "## Enumeration",
        f"- /users/{{owner}}/repos: {meta.get('count', 0)}",
        f"- token: GITHUB_TOKEN (workflow)",
        "",
        "## Highest risk (top)",
    ]
    
    for x in highest:
        lines.append(f"- {x['name']} | tag={x['tag']} | private={x['private']} | archived={x['archived']} | issues={x['open_issues']} | size_kb={x['size_kb']}")
    
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    
    # Append to RULES.md
    rules = Path("RULES.md")
    rules.touch(exist_ok=True)
    mark = "### GOVERNANCE (AUTO)"
    txt = rules.read_text(encoding="utf-8", errors="replace")
    
    if mark not in txt:
        txt += "\n\n" + mark + "\n- Runs recorded below.\n"
    
    txt += (
        f"\n- {now_iso()} | governance_v4_auto.py (GITHUB_TOKEN only)\n"
        f"  - total_repos={len(items)} top_n={top_n}\n"
        f"  - outputs: {out_json}, {out_md}\n"
    )
    
    rules.write_text(txt, encoding="utf-8")
    print("OK")

if __name__ == "__main__":
    main()
