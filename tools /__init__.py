"""
Tools package — all API integration tools.
"""
from tools.arxiv_tool import ArxivSearchTool, ArxivRSSFeedTool
from tools.semantic_scholar_tool import (
    SemanticScholarSearchTool,
    SemanticScholarAuthorTool,
    SemanticScholarReferenceTool,
)
from tools.reddit_tool import RedditSearchTool, RedditSubredditMonitorTool, RedditVacancyTool
from tools.github_tool import GitHubTrendingTool, GitHubRepoSearchTool, GitHubReleasesTool
from tools.hackernews_tool import HackerNewsSearchTool, HackerNewsWhoIsHiringTool
from tools.openalex_crossref_tool import OpenAlexSearchTool, OpenAlexInstitutionTool, CrossRefSearchTool
from tools.discord_tool import DiscordNotifyTool, DiscordWebhookPaperAlertTool
from tools.vacancy_tool import JobAggregatorTool, ProfileMatchScorerTool

__all__ = [
    "ArxivSearchTool", "ArxivRSSFeedTool",
    "SemanticScholarSearchTool", "SemanticScholarAuthorTool", "SemanticScholarReferenceTool",
    "RedditSearchTool", "RedditSubredditMonitorTool", "RedditVacancyTool",
    "GitHubTrendingTool", "GitHubRepoSearchTool", "GitHubReleasesTool",
    "HackerNewsSearchTool", "HackerNewsWhoIsHiringTool",
    "OpenAlexSearchTool", "OpenAlexInstitutionTool", "CrossRefSearchTool",
    "DiscordNotifyTool", "DiscordWebhookPaperAlertTool",
    "JobAggregatorTool", "ProfileMatchScorerTool",
]
