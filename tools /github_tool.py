"""
GitHub Search Tool — Free API (60 req/hour unauthenticated, 5000/hour with token).
Finds trending repos, new frameworks, AI agent libraries, and code implementations.
"""
import time
from typing import List, Dict, Any
from datetime import datetime, timedelta

import requests
from crewai.tools import BaseTool
from config import GITHUB_TOKEN


HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"


class GitHubTrendingTool(BaseTool):
    """Fetch trending AI/ML repositories from GitHub."""
    name: str = "github_trending"
    description: str = (
        "Finds trending GitHub repositories related to AI, ML, LLMs, computer vision, "
        "Agentic AI, MLOps. Input: topic keyword (e.g. 'agentic-ai', 'mlops', 'llm-agents')"
    )

    def _run(self, topic: str, max_results: int = 15) -> List[Dict[str, Any]]:
        results = []
        since = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

        try:
            # Search repos created recently with high stars
            resp = requests.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": f"{topic} created:>{since} stars:>10",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": max_results,
                },
                headers=HEADERS, timeout=15,
            )
            if resp.status_code == 200:
                for repo in resp.json().get("items", []):
                    results.append({
                        "source": "GitHub",
                        "name": repo["full_name"],
                        "description": (repo.get("description") or "")[:300],
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "language": repo.get("language", ""),
                        "topics": repo.get("topics", []),
                        "created_at": repo.get("created_at", ""),
                        "updated_at": repo.get("updated_at", ""),
                        "url": repo.get("html_url", ""),
                        "homepage": repo.get("homepage", ""),
                        "license": (repo.get("license") or {}).get("name", ""),
                    })
        except Exception as e:
            results.append({"error": f"GitHub search failed: {str(e)}", "source": "GitHub"})

        time.sleep(1)
        return results


class GitHubRepoSearchTool(BaseTool):
    """Search GitHub for specific AI frameworks, agent tools, and implementations."""
    name: str = "github_repo_search"
    description: str = (
        "Searches GitHub repositories by keyword. Use for finding specific "
        "AI frameworks, agent libraries, fine-tuning tools, etc. "
        "Input: search query (e.g. 'crewai agent framework' or 'world model JEPA')"
    )

    def _run(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        results = []
        try:
            resp = requests.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": max_results,
                },
                headers=HEADERS, timeout=15,
            )
            if resp.status_code == 200:
                for repo in resp.json().get("items", []):
                    results.append({
                        "source": "GitHub [search]",
                        "name": repo["full_name"],
                        "description": (repo.get("description") or "")[:300],
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "language": repo.get("language", ""),
                        "url": repo.get("html_url", ""),
                        "homepage": repo.get("homepage", ""),
                        "license": (repo.get("license") or {}).get("name", ""),
                    })
        except Exception as e:
            results.append({"error": f"GitHub repo search failed: {str(e)}", "source": "GitHub"})

        time.sleep(1)
        return results


class GitHubReleasesTool(BaseTool):
    """Get latest releases from key AI repos (Hugging Face, PyTorch, NVIDIA, etc.)."""
    name: str = "github_releases"
    description: str = (
        "Fetches the latest releases from major AI repositories. "
        "Input: comma-separated repo names (e.g. 'huggingface/transformers,pytorch/pytorch,nvidia/cuda-samples')"
    )

    def _run(self, repos: str, max_per_repo: int = 3) -> List[Dict[str, Any]]:
        all_results = []
        repo_list = [r.strip() for r in repos.split(",")]

        for repo_name in repo_list:
            try:
                resp = requests.get(
                    f"https://api.github.com/repos/{repo_name}/releases",
                    params={"per_page": max_per_repo},
                    headers=HEADERS, timeout=10,
                )
                if resp.status_code == 200:
                    for rel in resp.json():
                        all_results.append({
                            "source": f"GitHub Releases [{repo_name}]",
                            "tag": rel.get("tag_name", ""),
                            "name": rel.get("name", ""),
                            "body": (rel.get("body") or "")[:500],
                            "published_at": rel.get("published_at", ""),
                            "url": rel.get("html_url", ""),
                            "prerelease": rel.get("prerelease", False),
                        })
            except Exception as e:
                all_results.append({"error": f"GitHub releases for {repo_name}: {str(e)}", "source": "GitHub"})
            time.sleep(0.5)

        return all_results
