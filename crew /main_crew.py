"""
Main CrewAI Orchestration — Builds and runs the multi-agent research crew.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from crewai import Crew, Process

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OUTPUT_DIR, MAX_RESULTS_PER_SOURCE
from agents.research_agents import (
    academic_research_agent,
    industrial_research_agent,
    vacancy_scout_agent,
    social_media_agent,
    synthesis_agent,
)
from agents.tasks import (
    build_academic_tasks,
    build_industrial_tasks,
    build_social_media_tasks,
    build_vacancy_tasks,
    build_synthesis_task,
)


def build_tools_dict():
    """Instantiate all tools and return a dict mapping tool names to instances."""
    from tools import (
        ArxivSearchTool, ArxivRSSFeedTool,
        SemanticScholarSearchTool, SemanticScholarAuthorTool, SemanticScholarReferenceTool,
        RedditSearchTool, RedditSubredditMonitorTool, RedditVacancyTool,
        GitHubTrendingTool, GitHubRepoSearchTool, GitHubReleasesTool,
        HackerNewsSearchTool, HackerNewsWhoIsHiringTool,
        OpenAlexSearchTool, OpenAlexInstitutionTool, CrossRefSearchTool,
        DiscordNotifyTool, DiscordWebhookPaperAlertTool,
        JobAggregatorTool, ProfileMatchScorerTool,
    )

    return {
        # arXiv
        "arxiv_search": ArxivSearchTool(),
        "arxiv_rss": ArxivRSSFeedTool(),
        # Semantic Scholar
        "semantic_scholar_search": SemanticScholarSearchTool(),
        "semantic_scholar_author": SemanticScholarAuthorTool(),
        "semantic_scholar_ref": SemanticScholarReferenceTool(),
        # Reddit
        "reddit_search": RedditSearchTool(),
        "reddit_monitor": RedditSubredditMonitorTool(),
        "reddit_vacancy": RedditVacancyTool(),
        # GitHub
        "github_trending": GitHubTrendingTool(),
        "github_repo_search": GitHubRepoSearchTool(),
        "github_releases": GitHubReleasesTool(),
        # Hacker News
        "hackernews_search": HackerNewsSearchTool(),
        "hn_hiring": HackerNewsWhoIsHiringTool(),
        # OpenAlex & CrossRef
        "openalex_search": OpenAlexSearchTool(),
        "openalex_institution": OpenAlexInstitutionTool(),
        "crossref_search": CrossRefSearchTool(),
        # Discord
        "discord_notify": DiscordNotifyTool(),
        "discord_paper_alert": DiscordWebhookPaperAlertTool(),
        # Vacancies
        "job_aggregator": JobAggregatorTool(),
        "profile_scorer": ProfileMatchScorerTool(),
    }


def build_research_crew(mode: str = "full"):
    """
    Build the CrewAI Crew with agents and tasks.

    Modes:
      - "full"       : All agents, all tasks (default)
      - "academic"   : Academic research only
      - "industrial" : Industrial/framework tracking only
      - "vacancies"  : Job vacancy search only
      - "social"     : Social media monitoring only
    """
    tools_dict = build_tools_dict()

    all_tasks = []

    if mode in ("full", "academic"):
        all_tasks.extend(build_academic_tasks(tools_dict))

    if mode in ("full", "industrial"):
        all_tasks.extend(build_industrial_tasks(tools_dict))

    if mode in ("full", "social"):
        all_tasks.extend(build_social_media_tasks(tools_dict))

    if mode in ("full", "vacancies"):
        all_tasks.extend(build_vacancy_tasks(tools_dict))

    # Synthesis is always last
    all_tasks.append(build_synthesis_task(tools_dict))

    # Select agents based on mode
    agents_map = {
        "academic_agent": academic_research_agent,
        "industrial_agent": industrial_research_agent,
        "social_agent": social_media_agent,
        "vacancy_agent": vacancy_scout_agent,
        "synthesis_agent": synthesis_agent,
    }

    active_agents = set()
    if mode in ("full", "academic"):
        active_agents.add(academic_research_agent)
    if mode in ("full", "industrial"):
        active_agents.add(industrial_research_agent)
    if mode in ("full", "social"):
        active_agents.add(social_media_agent)
    if mode in ("full", "vacancies"):
        active_agents.add(vacancy_scout_agent)
    active_agents.add(synthesis_agent)  # Always include

    crew = Crew(
        agents=list(active_agents),
        tasks=all_tasks,
        verbose=True,
        process=Process.sequential,
        # memory=True,  # Enable for persistent memory across runs (requires crewai[extras])
    )

    return crew


def run_crew(mode: str = "full", output_file: str = None) -> str:
    """Run the research crew and save results."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, f"research_report_{timestamp}.md")

    print(f"\n{'='*60}")
    print(f"  Mohsen's AI Research Agent — Mode: {mode.upper()}")
    print(f"  Started at: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    crew = build_research_crew(mode=mode)

    print("Starting crew execution...\n")
    result = crew.kickoff()

    # Save report
    report_text = str(result)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# AI Research Intelligence Report\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n")
        f.write(f"**Mode:** {mode}\n\n")
        f.write(report_text)

    print(f"\n{'='*60}")
    print(f"  Report saved to: {output_file}")
    print(f"  Total characters: {len(report_text):,}")
    print(f"{'='*60}\n")

    return output_file


if __name__ == "__main__":
    import click

    @click.command()
    @click.option("--mode", "-m", type=click.Choice(["full", "academic", "industrial", "vacancies", "social"]),
                  default="full", help="Run mode")
    @click.option("--output", "-o", type=str, default=None, help="Output file path")
    def main(mode, output):
        run_crew(mode=mode, output_file=output)

    main()
