"""
Google ADK (Agent Development Kit) Integration Layer.

This module wraps the research agent system as ADK-compatible agents,
allowing deployment alongside or as an alternative to CrewAI.

Google ADK provides a standardized agent interface with:
- Tool registration
- Agent-to-agent communication
- State management
- Deployment to Google Cloud

Usage:
    python -m crew.adk_integration --mode full

Requirements:
    pip install google-adk
    export GOOGLE_API_KEY=<your-key>
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))


def create_adk_agent(name: str, description: str, tools: list, instruction: str):
    """
    Create a Google ADK-compatible agent definition.

    This returns a dict that can be used with ADK's Agent class,
    or serialized for deployment.
    """
    return {
        "name": name,
        "description": description,
        "tools": [t.name for t in tools],
        "instruction": instruction,
    }


def build_adk_agents():
    """
    Build the full set of ADK agents mirroring the CrewAI architecture.

    Returns a list of agent definitions ready for ADK deployment.
    """
    from tools import (
        ArxivSearchTool, ArxivRSSFeedTool,
        SemanticScholarSearchTool, SemanticScholarAuthorTool,
        RedditSearchTool, RedditSubredditMonitorTool, RedditVacancyTool,
        GitHubTrendingTool, GitHubRepoSearchTool, GitHubReleasesTool,
        HackerNewsSearchTool, HackerNewsWhoIsHiringTool,
        OpenAlexSearchTool, OpenAlexInstitutionTool,
        DiscordNotifyTool, JobAggregatorTool, ProfileMatchScorerTool,
    )

    agents = []

    # ── Academic Research Agent ──
    academic_tools = [ArxivSearchTool(), ArxivRSSFeedTool(),
                      SemanticScholarSearchTool(), SemanticScholarAuthorTool(),
                      OpenAlexSearchTool(), OpenAlexInstitutionTool()]
    agents.append(create_adk_agent(
        name="academic_research_agent",
        description="Finds novel academic papers on Physical AI, World Models, Robotics, and Geometric DL from Yann LeCun's labs and top institutions.",
        tools=academic_tools,
        instruction=(
            "You are an academic research scout specializing in Physical AI, World Models, "
            "JEPA architectures, Geometric Deep Learning, and Robotics AI. Track papers from "
            "Yann LeCun, NYU AIM Lab, Meta FAIR, DeepMind, MIT CSAIL, Stanford, ETH, CMU. "
            "Search arXiv, Semantic Scholar, and OpenAlex. Return structured results with "
            "relevance scoring for Mohsen Mostafa's Physical & Geometric AI research program."
        ),
    ))

    # ── Industrial Research Agent ──
    industrial_tools = [GitHubTrendingTool(), GitHubRepoSearchTool(), GitHubReleasesTool(),
                        HackerNewsSearchTool(), SemanticScholarSearchTool()]
    agents.append(create_adk_agent(
        name="industrial_research_agent",
        description="Tracks industrial AI developments: LLMs, Agentic AI frameworks, MLOps, NVIDIA tools, fine-tuning.",
        tools=industrial_tools,
        instruction=(
            "You are an industrial AI technology scout. Track new frameworks (CrewAI, LangGraph, "
            "Google ADK), LLM optimizations, fine-tuning techniques, MLOps tools, NVIDIA releases. "
            "Search GitHub trending, Hacker News, and Semantic Scholar. Focus on production-ready "
            "tools relevant to Mohsen Mostafa's work with TensorRT/ONNX, RAG pipelines, and MLOps."
        ),
    ))

    # ── Social Media Agent ──
    social_tools = [RedditSearchTool(), RedditSubredditMonitorTool(),
                    HackerNewsSearchTool()]
    agents.append(create_adk_agent(
        name="social_media_agent",
        description="Monitors Reddit and Hacker News for AI community discussions, trending topics, and new releases.",
        tools=social_tools,
        instruction=(
            "Monitor AI communities on Reddit (r/MachineLearning, r/deeplearning, r/LocalLLaMA, "
            "r/MLOps, r/robotics, r/ComputerVision) and Hacker News. Identify trending discussions, "
            "new open-source tools, and community insights. Track engagement metrics."
        ),
    ))

    # ── Vacancy Scout Agent ──
    vacancy_tools = [JobAggregatorTool(), HackerNewsWhoIsHiringTool(),
                     RedditVacancyTool(), ProfileMatchScorerTool()]
    agents.append(create_adk_agent(
        name="vacancy_scout_agent",
        description="Finds and ranks AI/ML job vacancies matching Mohsen Mostafa's profile.",
        tools=vacancy_tools,
        instruction=(
            "Find AI/ML/CV/Robotics job vacancies matching Mohsen Mostafa: AI Team Lead, "
            "Research Engineer, 8+ years AI/ML, 6+ papers on Physical & Geometric AI, "
            "PyTorch, LLMs, RAG, MLOps, Kubernetes. Search HN Who is Hiring, Reddit, "
            "and job aggregators. Score and rank by profile match."
        ),
    ))

    # ── Synthesis Agent ──
    synthesis_tools = [DiscordNotifyTool()]
    agents.append(create_adk_agent(
        name="synthesis_agent",
        description="Synthesizes all findings into a structured, actionable research intelligence report.",
        tools=synthesis_tools,
        instruction=(
            "Synthesize all agent findings into a structured report:\n"
            "1. Executive Summary (top highlights)\n"
            "2. Top Academic Papers (ranked by relevance)\n"
            "3. Industrial Developments\n"
            "4. Trending Repos & Frameworks\n"
            "5. Community Highlights\n"
            "6. Vacancy Alerts (ranked by match)\n"
            "7. Recommended Actions\n"
            "Rank everything by relevance to Mohsen's Physical & Geometric AI research."
        ),
    ))

    return agents


def run_adk_mode(mode: str = "full"):
    """
    Run agents using Google ADK architecture (when ADK is available).

    Falls back to direct tool execution if ADK is not installed.
    """
    try:
        from google.adk import Agent as AdkAgent
        from google.adk.runners import Runner
        ADK_AVAILABLE = True
    except ImportError:
        ADK_AVAILABLE = False
        print("Google ADK not installed. Running in standalone mode with direct tool calls.")
        print("Install with: pip install google-adk\n")

    agents_config = build_adk_agents()

    if not ADK_AVAILABLE:
        # Fallback: run tools directly and aggregate
        return _run_standalone(mode, agents_config)

    # ADK mode: create proper ADK agents
    # This is the production path when ADK is installed
    print(f"Running with Google ADK — Mode: {mode}\n")
    print(f"Available agents: {[a['name'] for a in agents_config]}")
    print("\nTo deploy with ADK, use the agent configs in build_adk_agents().")
    print("See ADK documentation for deployment options: Vertex AI, Cloud Run, etc.")

    return agents_config


def _run_standalone(mode: str, agents_config: list):
    """
    Standalone execution without ADK — runs tools directly and aggregates results.
    This is useful for testing and when ADK is not installed.
    """
    from tools import (
        ArxivSearchTool, SemanticScholarSearchTool, SemanticScholarAuthorTool,
        OpenAlexInstitutionTool, GitHubTrendingTool, HackerNewsSearchTool,
        HackerNewsWhoIsHiringTool, RedditVacancyTool, JobAggregatorTool,
        ProfileMatchScorerTool,
    )
    from config import ACADEMIC_QUERIES, OUTPUT_DIR

    all_results = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n{'='*60}")
    print(f"  Standalone Mode — {mode.upper()}")
    print(f"  {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    # Academic
    if mode in ("full", "academic"):
        print("[1/5] Searching arXiv for Physical AI & World Models papers...")
        arxiv = ArxivSearchTool()
        papers = arxiv._run("physical AI world model JEPA embodied", max_results=5)
        all_results["arxiv_papers"] = papers
        print(f"  Found {len([p for p in papers if 'error' not in p])} papers\n")

        print("[2/5] Tracking Yann LeCun via Semantic Scholar...")
        ss_author = SemanticScholarAuthorTool()
        lecitin_papers = ss_author._run("Yann LeCun", max_results=5)
        all_results["lecun_papers"] = lecitin_papers
        print(f"  Found {len([p for p in lecitin_papers if 'error' not in p])} papers\n")

        print("[3/5] Searching NYU/Meta FAIR via OpenAlex...")
        openalex = OpenAlexInstitutionTool()
        nyu_papers = openalex._run("New York University", max_results=5)
        all_results["nyu_papers"] = nyu_papers
        print(f"  Found {len([p for p in nyu_papers if 'error' not in p])} papers\n")

    # Industrial
    if mode in ("full", "industrial"):
        print("[4/5] Checking GitHub trending AI repos...")
        gh = GitHubTrendingTool()
        repos = gh._run("agentic-ai", max_results=5)
        all_results["trending_repos"] = repos
        print(f"  Found {len([r for r in repos if 'error' not in r])} repos\n")

    # Vacancies
    if mode in ("full", "vacancies"):
        print("[5/5] Searching for AI vacancies...")
        hn_hiring = HackerNewsWhoIsHiringTool()
        hiring = hn_hiring._run("", max_results=10)
        all_results["hiring"] = hiring
        print(f"  Found {len([h for h in hiring if 'error' not in h])} leads\n")

    # Save raw results
    output_file = os.path.join(OUTPUT_DIR, f"standalone_results_{timestamp}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str, ensure_ascii=False)

    print(f"Raw results saved to: {output_file}")
    print(f"\nTotal items collected: {sum(len(v) for v in all_results.values())}")

    return all_results


if __name__ == "__main__":
    import click

    @click.command()
    @click.option("--mode", "-m", type=click.Choice(["full", "academic", "industrial", "vacancies", "social"]),
                  default="full", help="Run mode")
    def main(mode):
        run_adk_mode(mode=mode)

    main()
