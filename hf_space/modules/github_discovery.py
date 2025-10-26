
"""
GitHub discovery and scoring utilities using the GraphQL API.
"""
from __future__ import annotations

import os
import json
import math
from datetime import datetime
from typing import List, Dict, Any, Optional

import httpx


async def search_github_users(
    languages: List[str],
    min_repos: int = 3,
    min_followers: int = 10,
    github_token: Optional[str] = None,
    target_count: int = 20,
) -> List[Dict[str, Any]]:
    """
    Search GitHub for users using GraphQL, filtered by languages and repos.
    Location is omitted for now (not tracked in current job model).
    """
    token = github_token or os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GitHub token not configured for GraphQL discovery")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    all_users: Dict[str, Dict[str, Any]] = {}

    lang_list = languages or [""]

    per_page = max(5, min(20, target_count))
    max_pages_default = 3

    async with httpx.AsyncClient(timeout=15.0) as client:
        for lang in lang_list:
            query_parts = ["type:user", f"repos:>={min_repos}"]
            if min_followers and min_followers > 0:
                query_parts.append(f"followers:>={min_followers}")
            if lang:
                query_parts.append(f"language:{lang}")
            search_query = " ".join(query_parts)

            cursor = None
            has_next = True
            pages_fetched = 0
            max_pages = max(1, min(max_pages_default, (target_count + per_page - 1) // per_page))

            while has_next and pages_fetched < max_pages:
                graphql_query = """
                query($searchQuery: String!, $cursor: String) {
                  search(query: $searchQuery, type: USER, first: PER_PAGE, after: $cursor) {
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      ... on User {
                        login
                        name
                        location
                        followers { totalCount }
                        repositories(first: 3, orderBy: {field: STARGAZERS, direction: DESC}, isFork: false) {
                          nodes {
                            name
                            primaryLanguage { name }
                            stargazerCount
                            updatedAt
                            repositoryTopics(first: 5) { nodes { topic { name } } }
                          }
                        }
                        contributionsCollection {
                          totalCommitContributions
                          totalPullRequestContributions
                          totalIssueContributions
                        }
                      }
                    }
                  }
                }
                """.replace("PER_PAGE", str(per_page))
                variables = {"searchQuery": search_query, "cursor": cursor}

                resp = await client.post(
                    "https://api.github.com/graphql",
                    headers=headers,
                    json={"query": graphql_query, "variables": variables},
                )
                if resp.status_code != 200:
                    # Unauthorized or forbidden: abort fast so caller can fallback
                    if resp.status_code in (401, 403):
                        raise RuntimeError(f"GitHub GraphQL error {resp.status_code}: {resp.text[:120]}")
                    # Other errors: continue to next page/language
                    continue
                data = resp.json()
                search_results = data.get("data", {}).get("search", {})
                if not search_results:
                    break

                users = search_results.get("nodes", [])
                for user in users:
                    if user and user.get("login") and user["login"] not in all_users:
                        all_users[user["login"]] = user

                # Early stop if we already have enough users
                if len(all_users) >= target_count:
                    has_next = False
                    break

                page_info = search_results.get("pageInfo", {})
                has_next = page_info.get("hasNextPage", False)
                cursor = page_info.get("endCursor")
                pages_fetched += 1

            # Early stop across languages as soon as we have enough
            if len(all_users) >= target_count:
                break

    return list(all_users.values())


def score_user(user: Dict[str, Any], jd_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Score a GitHub user against JD spec (0-100) with subscores and reasons."""
    jd_languages = set(jd_spec.get("languages", []))
    jd_topics = set(jd_spec.get("topics", []))

    user_languages = set()
    user_topics = set()
    max_stars = 0
    most_recent_update: Optional[datetime] = None

    repos = user.get("repositories", {}).get("nodes", [])
    for repo in repos:
        if repo:
            if repo.get("primaryLanguage") and repo["primaryLanguage"].get("name"):
                user_languages.add(repo["primaryLanguage"]["name"].lower())
            for tnode in repo.get("repositoryTopics", {}).get("nodes", []):
                if tnode and tnode.get("topic"):
                    user_topics.add(tnode["topic"]["name"].lower())
            max_stars = max(max_stars, repo.get("stargazerCount", 0))
            upd = repo.get("updatedAt")
            if upd:
                dt = datetime.fromisoformat(upd.replace("Z", "+00:00"))
                if most_recent_update is None or dt > most_recent_update:
                    most_recent_update = dt

    # Skills (60%)
    lang_match = len(jd_languages & user_languages)
    topic_match = len(jd_topics & user_topics)
    total_skills = len(jd_languages) + len(jd_topics)
    skill_score = ((lang_match + topic_match) / total_skills) * 60 if total_skills > 0 else 0

    # Activity (25%)
    contrib = user.get("contributionsCollection", {})
    total_activity = (
        contrib.get("totalCommitContributions", 0)
        + contrib.get("totalPullRequestContributions", 0)
        + contrib.get("totalIssueContributions", 0)
    )
    activity_base = min(math.log(total_activity + 1) / math.log(1000), 1) * 15
    recency_bonus = 0
    if most_recent_update:
        days_ago = (datetime.now(most_recent_update.tzinfo) - most_recent_update).days
        if days_ago <= 90:
            recency_bonus = 10
    activity_score = activity_base + recency_bonus

    # Quality (10%)
    followers = user.get("followers", {}).get("totalCount", 0)
    quality_score = min(math.log(max_stars + followers + 1) / math.log(1000), 1) * 10

    # Completeness (5%)
    completeness_score = (2.5 if user.get("name") else 0) + (2.5 if user.get("location") else 0)

    total_score = min(max(skill_score + activity_score + quality_score + completeness_score, 0), 100)

    reasons = []
    if lang_match > 0:
        reasons.append(f"{lang_match} language match(es)")
    if topic_match > 0:
        reasons.append(f"{topic_match} topic match(es)")
    if total_activity > 100:
        reasons.append(f"{total_activity} contributions last year")
    if recency_bonus > 0:
        reasons.append("Recent activity (≤90 days)")
    if max_stars > 50:
        reasons.append(f"Top repo has {max_stars} stars")
    if followers > 20:
        reasons.append(f"{followers} followers")

    return {
        "total_score": round(total_score, 1),
        "technical_skills_score": round(skill_score, 1),
        "experience_score": 0.0,
        "activity_score": round(activity_score, 1),
        "education_score": 0.0,
        "soft_skills_score": 0.0,
        "reasons": reasons,
        "user_languages": sorted(list(user_languages)),
        "user_topics": sorted(list(user_topics)),
        "followers": followers,
        "max_stars": max_stars,
    }


def map_technical_to_languages(technical: List[str]) -> List[str]:
    """Map technical terms/frameworks to GitHub primary language names.

    Covers common stacks so discovery isn't overly strict.
    """
    if not technical:
        return []
    lang_set = set()
    # Direct languages and common aliases/frameworks
    alias_map = {
        # Languages
        "python": "python",
        "javascript": "javascript",
        "typescript": "typescript",
        "java": "java",
        "go": "go",
        "golang": "go",
        "rust": "rust",
        "ruby": "ruby",
        "php": "php",
        "c++": "c++",
        "c#": "c#",
        "dotnet": "c#",
        ".net": "c#",
        "scala": "scala",
        "kotlin": "kotlin",
        "swift": "swift",
        # Python frameworks
        "django": "python",
        "flask": "python",
        "fastapi": "python",
        "pandas": "python",
        "numpy": "python",
        # JS frameworks
        "react": "javascript",
        "next.js": "javascript",
        "nextjs": "javascript",
        "node": "javascript",
        "node.js": "javascript",
        "express": "javascript",
        "angular": "javascript",
        "vue": "javascript",
        "nuxt": "javascript",
        "svelte": "javascript",
        # Java frameworks
        "spring": "java",
        "spring boot": "java",
        # Others
        "rails": "ruby",
        "laravel": "php",
        "symfony": "php",
    }
    tech_lower = [t.lower() for t in technical]
    for t in tech_lower:
        for k, v in alias_map.items():
            if k in t:
                lang_set.add(v)
    # Sensible fallback for web/backend roles
    if not lang_set:
        joined = " ".join(tech_lower)
        if any(x in joined for x in ["django", "fastapi", "flask", "python"]):
            lang_set.add("python")
        if any(x in joined for x in ["react", "node", "angular", "vue", "typescript", "javascript"]):
            lang_set.add("javascript")
            if "typescript" in joined:
                lang_set.add("typescript")
        if any(x in joined for x in ["spring", "java"]):
            lang_set.add("java")
    return sorted(list(lang_set))


async def discover_candidates_for_job(
    technical: List[str],
    max_candidates: int = 20,
    github_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Discover and score candidates for given technical requirements.
    Returns list of candidate dicts compatible with current UI.
    """
    languages = map_technical_to_languages(technical)
    users = await search_github_users(
        languages=languages,
        min_repos=3,
        min_followers=10,
        github_token=github_token,
        target_count=max_candidates,
    )

    jd_spec = {"languages": languages, "topics": []}

    results: List[Dict[str, Any]] = []
    for user in users:
        s = score_user(user, jd_spec)

        # Build portfolio and details
        portfolio = []
        max_stars = 0
        repos = user.get("repositories", {}).get("nodes", [])
        for repo in repos:
            if repo:
                repo_data = {
                    "name": repo.get("name", ""),
                    "stars": repo.get("stargazerCount", 0),
                    "language": (repo.get("primaryLanguage") or {}).get("name"),
                    "topics": [tn["topic"]["name"] for tn in (repo.get("repositoryTopics", {}) or {}).get("nodes", []) if tn and tn.get("topic")],
                    "updated_at": repo.get("updatedAt", ""),
                }
                max_stars = max(max_stars, repo_data["stars"])
                portfolio.append(repo_data)

        results.append({
            "login": user.get("login", ""),
            "name": user.get("name") or user.get("login", ""),
            "location": user.get("location", ""),
            "followers": s.get("followers", 0),
            "total_stars": max_stars,
            "portfolio": portfolio,
            "langsFound": s.get("user_languages", []),
            "topicsFound": s.get("user_topics", []),
            "reasons": s.get("reasons", []),
            "score": s.get("total_score", 0.0),
        })

    # Sort by score desc and trim
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:max_candidates]
