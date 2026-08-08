#!/usr/bin/env python3
"""
Fetches real GitHub profile stats (stars, commits, repos, followers,
top languages, PR count, account age) and writes them to stats_data.json
for the generate_*.py scripts to consume.

Requires:
  GH_USERNAME   - the GitHub username to fetch stats for
  GH_TOKEN      - a token with at least `read:user` scope (a classic PAT).
                  Falls back to unauthenticated public REST calls (lower
                  rate limits, no commit-contribution data) if not set.
"""
import os
import sys
import json
import time
from datetime import datetime, timezone
import urllib.request
import urllib.error

USERNAME = os.environ.get("GH_USERNAME")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

if not USERNAME:
    print("GH_USERNAME is required", file=sys.stderr)
    sys.exit(1)

API = "https://api.github.com"
GRAPHQL = "https://api.github.com/graphql"


def rest(path, params=None):
    url = f"{API}{path}"
    if params:
        from urllib.parse import urlencode
        url += "?" + urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "profile-stats-script")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def graphql(query, variables=None):
    if not TOKEN:
        return None
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(GRAPHQL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("User-Agent", "profile-stats-script")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print("GraphQL error:", e.read().decode(), file=sys.stderr)
        return None


def get_user_profile():
    return rest(f"/users/{USERNAME}")


def get_all_owned_repos():
    repos = []
    page = 1
    while True:
        batch = rest(f"/users/{USERNAME}/repos", {"per_page": 100, "page": page, "type": "owner"})
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > 10:  # safety cap
            break
    return [r for r in repos if not r.get("fork")]


def get_language_bytes(repos):
    totals = {}
    for r in repos:
        lang_url = r.get("languages_url")
        if not lang_url:
            continue
        path = lang_url.replace(API, "")
        try:
            langs = rest(path)
        except Exception:
            continue
        for lang, byte_count in langs.items():
            totals[lang] = totals.get(lang, 0) + byte_count
        time.sleep(0.05)
    return totals


def get_pr_count():
    try:
        res = rest("/search/issues", {"q": f"author:{USERNAME} type:pr", "per_page": 1})
        return res.get("total_count", 0)
    except Exception:
        return 0


def get_lifetime_commits(created_at_iso):
    """Sums totalCommitContributions (+ restricted/private if token scope allows)
    year by year, since GitHub's contributionsCollection only accepts <=1yr ranges."""
    if not TOKEN:
        return None
    start_year = datetime.fromisoformat(created_at_iso.replace("Z", "+00:00")).year
    end_year = datetime.now(timezone.utc).year
    total = 0
    query = """
    query($from: DateTime!, $to: DateTime!) {
      viewer {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    for year in range(start_year, end_year + 1):
        frm = f"{year}-01-01T00:00:00Z"
        to = f"{year}-12-31T23:59:59Z"
        data = graphql(query, {"from": frm, "to": to})
        if not data or "data" not in data or not data["data"]:
            continue
        cc = data["data"]["viewer"]["contributionsCollection"]
        total += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    return total


def rank_for(value, thresholds):
    """thresholds: list of (min_value, label) sorted descending by min_value."""
    for min_val, label in thresholds:
        if value >= min_val:
            return label
    return thresholds[-1][1]


def main():
    profile = get_user_profile()
    repos = get_all_owned_repos()

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_repos = profile.get("public_repos", len(repos))
    followers = profile.get("followers", 0)
    created_at = profile.get("created_at")

    lang_bytes = get_language_bytes(repos)
    lang_total = sum(lang_bytes.values()) or 1
    top_langs = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)[:6]
    top_langs_pct = [(name, round(b / lang_total * 100, 1)) for name, b in top_langs]

    pr_count = get_pr_count()

    commits = get_lifetime_commits(created_at) if created_at else None
    commits_is_estimate = commits is None
    if commits is None:
        # unauthenticated fallback: no reliable lifetime commit count available
        commits = 0

    now = datetime.now(timezone.utc)
    created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else now
    experience_years = max(1, round((now - created_dt).days / 365))

    trophies = [
        ("Commits", commits, rank_for(commits, [(3000, "SSS"), (1500, "SS"), (800, "S"), (300, "A+"), (100, "A"), (0, "B")])),
        ("Stars", total_stars, rank_for(total_stars, [(500, "SSS"), (200, "SS"), (80, "S"), (30, "A+"), (10, "A"), (0, "B")])),
        ("Followers", followers, rank_for(followers, [(500, "SSS"), (200, "SS"), (80, "S"), (30, "A+"), (10, "A"), (0, "B")])),
        ("Repositories", total_repos, rank_for(total_repos, [(60, "SSS"), (35, "SS"), (20, "S"), (10, "A+"), (5, "A"), (0, "B")])),
        ("Experience", experience_years, rank_for(experience_years, [(8, "SSS"), (5, "SS"), (3, "S"), (2, "A+"), (1, "A"), (0, "B")])),
        ("PullRequest", pr_count, rank_for(pr_count, [(300, "SSS"), (150, "SS"), (60, "S"), (20, "A+"), (5, "A"), (0, "B")])),
    ]

    data = {
        "generated_at": now.isoformat(),
        "username": USERNAME,
        "total_stars": total_stars,
        "total_commits": commits,
        "commits_is_estimate": commits_is_estimate,
        "total_repos": total_repos,
        "followers": followers,
        "pr_count": pr_count,
        "experience_years": experience_years,
        "top_languages": top_langs_pct,
        "trophies": trophies,
    }

    with open("stats_data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()