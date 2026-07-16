"""
Hacker News API Tool — Completely free, no API key needed.
Fetches stories about AI, ML, research papers, and job postings.
"""
import time
from typing import List, Dict, Any

import requests
from crewai.tools import BaseTool


HN_API = "https://hacker-news.firebaseio.com/v0"


class HackerNewsSearchTool(BaseTool):
    """Search HN for AI-related stories using Algolia HN Search API (free)."""
    name: str = "hackernews_search"
    description: str = (
        "Searches Hacker News for AI/ML research, frameworks, tools, and discussions. "
        "Input: search query (e.g. 'agentic AI framework' or 'world model Yann LeCun')"
    )

    def _run(self, query: str, max_results: int = 15) -> List[Dict[str, Any]]:
        results = []
        try:
            resp = requests.get(
                "https://hn.algolia.com/api/v1/search",
                params={
                    "query": query,
                    "tags": "story",
                    "numericFilters": "points>5",
                    "hitsPerPage": max_results,
                },
                timeout=15,
            )
            if resp.status_code == 200:
                for hit in resp.json().get("hits", []):
                    results.append({
                        "source": "Hacker News",
                        "title": hit.get("title", ""),
                        "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                        "hn_url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                        "points": hit.get("points", 0),
                        "num_comments": hit.get("num_comments", 0),
                        "author": hit.get("author", ""),
                        "created_at": hit.get("created_at", ""),
                    })
        except Exception as e:
            results.append({"error": f"HN search failed: {str(e)}", "source": "Hacker News"})

        return results


class HackerNewsWhoIsHiringTool(BaseTool):
    """Fetch the monthly 'Ask HN: Who is Hiring' threads — goldmine for AI jobs."""
    name: str = "hackernews_who_is_hiring"
    description: str = (
        "Fetches the monthly 'Who is Hiring' threads from Hacker News and filters "
        "for AI/ML/CV related positions. No input needed — pass any string."
    )

    def _run(self, _: str = "", max_results: int = 50) -> List[Dict[str, Any]]:
        results = []
        ai_keywords = [
            "ai", "ml", "machine learning", "deep learning", "computer vision",
            "llm", "nlp", "robotics", "mlops", "data scientist", "research scientist",
            "agentic", "generative ai", "pytorch", "tensorflow",
        ]

        try:
            # Search for "Who is Hiring" posts
            resp = requests.get(
                "https://hn.algolia.com/api/v1/search",
                params={
                    "query": "Who is hiring",
                    "tags": "story",
                    "hitsPerPage": 3,
                },
                timeout=15,
            )
            if resp.status_code != 200:
                return [{"error": "HN Who is Hiring fetch failed", "source": "Hacker News"}]

            for hit in resp.json().get("hits", []):
                story_id = hit.get("objectID")
                title = hit.get("title", "")

                # Get comments of the hiring thread
                comments_resp = requests.get(
                    f"https://hn.algolia.com/api/v1/search",
                    params={
                        "tags": f"comment,story_{story_id}",
                        "hitsPerPage": 200,
                    },
                    timeout=20,
                )
                if comments_resp.status_code != 200:
                    continue

                for comment in comments_resp.json().get("hits", []):
                    text = comment.get("comment_text", "").lower()
                    if any(kw in text for kw in ai_keywords):
                        results.append({
                            "source": f"HN Who is Hiring [{title}]",
                            "comment_text": comment.get("comment_text", "")[:500],
                            "author": comment.get("author", ""),
                            "url": f"https://news.ycombinator.com/item?id={comment.get('objectID')}",
                            "parent_title": title,
                        })
                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break

        except Exception as e:
            results.append({"error": f"HN Who is Hiring failed: {str(e)}", "source": "Hacker News"})

        return results
