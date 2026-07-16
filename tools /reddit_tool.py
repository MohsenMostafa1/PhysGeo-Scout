"""
Reddit Tool — Free via PRAW (requires app registration).
Monitors subreddits for research papers, frameworks, job posts, and discussions.
"""
import time
from typing import List, Dict, Any

from crewai.tools import BaseTool
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT


def _get_reddit_instance():
    """Lazily create Reddit instance."""
    try:
        import praw
        if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
            return praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
            )
        else:
            # Read-only instance — limited but works for public content
            return praw.Reddit(
                client_id=REDDIT_CLIENT_ID or None,
                client_secret=REDDIT_CLIENT_SECRET or None,
                user_agent=REDDIT_USER_AGENT,
            )
    except Exception:
        return None


class RedditSearchTool(BaseTool):
    name: str = "reddit_search"
    description: str = (
        "Searches Reddit for posts about AI research, papers, frameworks, job vacancies. "
        "Monitors r/MachineLearning, r/deeplearning, r/LocalLLaMA, r/MLOps, etc. "
        "Input: search query string."
    )

    def _run(self, query: str, subreddit: str = "all", max_results: int = 15) -> List[Dict[str, Any]]:
        reddit = _get_reddit_instance()
        if not reddit:
            return [{"error": "Reddit not configured. Set REDDIT_CLIENT_ID/SECRET in .env", "source": "Reddit"}]

        results = []
        try:
            sub = reddit.subreddit(subreddit)
            for post in sub.search(query, sort="new", time_filter="week", limit=max_results):
                results.append({
                    "source": f"Reddit r/{subreddit}",
                    "title": post.title,
                    "author": str(post.author) if post.author else "[deleted]",
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "created_utc": post.created_utc,
                    "selftext": post.selftext[:400] if post.selftext else "",
                    "link_flair": post.link_flair_text or "",
                    "is_video": post.is_video,
                    "external_url": post.url if post.url and not post.url.startswith("https://www.reddit.com") else "",
                })
        except Exception as e:
            results.append({"error": f"Reddit search failed: {str(e)}", "source": "Reddit"})

        time.sleep(0.5)
        return results


class RedditSubredditMonitorTool(BaseTool):
    """Monitor specific subreddits' newest posts (no search query, just latest)."""
    name: str = "reddit_subreddit_monitor"
    description: str = (
        "Fetches the newest posts from specific subreddits. "
        "Input: comma-separated subreddit names (e.g. 'MachineLearning,deeplearning,LocalLLaMA')"
    )

    def _run(self, subreddits: str, max_per_sub: int = 10) -> List[Dict[str, Any]]:
        reddit = _get_reddit_instance()
        if not reddit:
            return [{"error": "Reddit not configured. Set REDDIT_CLIENT_ID/SECRET in .env", "source": "Reddit"}]

        all_results = []
        sub_list = [s.strip() for s in subreddits.split(",")]

        for sub_name in sub_list:
            try:
                sub = reddit.subreddit(sub_name)
                for post in sub.new(limit=max_per_sub):
                    all_results.append({
                        "source": f"Reddit r/{sub_name}",
                        "title": post.title,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "url": f"https://reddit.com{post.permalink}",
                        "created_utc": post.created_utc,
                        "selftext": post.selftext[:300] if post.selftext else "",
                        "link_flair": post.link_flair_text or "",
                        "external_url": post.url if not post.url.startswith("https://www.reddit.com") else "",
                    })
            except Exception as e:
                all_results.append({"error": f"r/{sub_name} failed: {str(e)}", "source": "Reddit"})
            time.sleep(0.5)

        return all_results


class RedditVacancyTool(BaseTool):
    """Specialized tool for finding job/vacancy posts on Reddit."""
    name: str = "reddit_vacancy_search"
    description: str = (
        "Searches Reddit specifically for AI/ML job vacancies and hiring posts. "
        "Searches across multiple job-related subreddits. "
        "Input: comma-separated role keywords (e.g. 'AI Research Engineer,ML Engineer')"
    )

    def _run(self, role_keywords: str, max_results: int = 30) -> List[Dict[str, Any]]:
        reddit = _get_reddit_instance()
        if not reddit:
            return [{"error": "Reddit not configured", "source": "Reddit"}]

        job_subreddits = [
            "MachineLearning", "deeplearning", "cscareerquestions",
            "dataengineering", "artificial", "jobs", "careerguidance",
        ]
        keywords = [k.strip() for k in role_keywords.split(",")]
        results = []
        seen_urls = set()

        for sub_name in job_subreddits:
            for kw in keywords:
                try:
                    sub = reddit.subreddit(sub_name)
                    for post in sub.search(kw, sort="new", time_filter="month", limit=5):
                        url = f"https://reddit.com{post.permalink}"
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)

                        results.append({
                            "source": f"Reddit r/{sub_name} [vacancy]",
                            "title": post.title,
                            "company_hint": "",
                            "location_hint": "remote" if "remote" in post.title.lower() else "",
                            "url": url,
                            "score": post.score,
                            "created_utc": post.created_utc,
                            "selftext": post.selftext[:500] if post.selftext else "",
                        })
                except Exception:
                    pass
                time.sleep(0.3)

        return results[:max_results]
