"""
Mohsen's AI Research & Vacancy Agent System
Entry Point — CLI with scheduling support.

Usage:
    python run.py                    # Full run (all agents)
    python run.py -m academic        # Academic papers only
    python run.py -m industrial      # Industrial tools only
    python run.py -m vacancies       # Job search only
    python run.py -m social          # Social media only
    python run.py --adk              # Use Google ADK mode
    python run.py --schedule 6       # Run every 6 hours
    python run.py --test             # Quick test run
"""
import os
import sys
import time
import signal
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Ensure project root on path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

console = Console()

BANNER = r"""
[bold cyan]
╔══════════════════════════════════════════════════════════════╗
║        MOHSEN'S AI RESEARCH INTELLIGENCE AGENT             ║
║     Powered by CrewAI + Google ADK + 10+ Free APIs         ║
╚══════════════════════════════════════════════════════════════╝
[/bold cyan]
"""

API_STATUS_TABLE = """
[bold]Free API Sources (no key required):[/bold]
  ✅ arXiv API          — Papers & preprints
  ✅ Semantic Scholar   — Citations & author tracking
  ✅ OpenAlex           — Open scholarly metadata
  ✅ CrossRef           — DOI metadata
  ✅ Hacker News        — Stories & Who is Hiring
  ✅ GitHub API         — Repos & releases (60 req/hour)

[bold]APIs with optional free keys:[/bold]
  🔑 Reddit (PRAW)     — Community discussions
  🔑 GitHub Token      — 5000 req/hour (vs 60)
  🔑 Semantic Scholar   — Higher rate limits
  🔑 Discord Webhook   — Notifications

[bold]APIs requiring setup:[/bold]
  🔐 Google ADK        — Agent deployment platform
"""

_running = True


def _signal_handler(sig, frame):
    global _running
    _running = False
    console.print("\n[yellow]Scheduled run interrupted. Shutting down...[/yellow]")


def check_environment():
    """Check which APIs are configured and show status."""
    from dotenv import load_dotenv
    load_dotenv()

    table = Table(title="API Configuration Status")
    table.add_column("API", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Notes")

    checks = [
        ("arXiv", os.getenv("REDDIT_CLIENT_ID") or True, "Always available"),
        ("Semantic Scholar", True, "Works without key (rate limited)"),
        ("OpenAlex", True, "Always available"),
        ("CrossRef", True, "Always available"),
        ("Hacker News", True, "Always available"),
        ("GitHub", bool(os.getenv("GITHUB_TOKEN")), "Token → 5000 req/h"),
        ("Reddit", bool(os.getenv("REDDIT_CLIENT_ID")), "Needs app registration"),
        ("Discord", bool(os.getenv("DISCORD_WEBHOOK_URL")), "Needs webhook URL"),
        ("Google ADK", bool(os.getenv("GOOGLE_API_KEY")), "Needs API key"),
        ("OpenAI (LLM)", bool(os.getenv("OPENAI_API_KEY")), "For CrewAI agents"),
    ]

    for name, configured, notes in checks:
        status = "[green]✅ Ready[/green]" if configured else "[yellow]⚠ Not configured[/yellow]"
        table.add_row(name, status, notes)

    console.print(table)


def run_test():
    """Quick test: verify all free APIs are reachable."""
    console.print(Panel("[bold]Running API Connectivity Test...[/bold]", border_style="blue"))

    tests = []

    # arXiv
    try:
        from tools.arxiv_tool import ArxivSearchTool
        t = ArxivSearchTool()
        r = t._run("world model", max_results=2)
        ok = len([x for x in r if "error" not in x]) > 0
        tests.append(("arXiv Search", ok, f"{len(r)} results"))
    except Exception as e:
        tests.append(("arXiv Search", False, str(e)[:80]))

    # Semantic Scholar
    try:
        from tools.semantic_scholar_tool import SemanticScholarSearchTool
        t = SemanticScholarSearchTool()
        r = t._run("physical AI", max_results=2)
        ok = len([x for x in r if "error" not in x]) > 0
        tests.append(("Semantic Scholar", ok, f"{len(r)} results"))
    except Exception as e:
        tests.append(("Semantic Scholar", False, str(e)[:80]))

    # GitHub
    try:
        from tools.github_tool import GitHubTrendingTool
        t = GitHubTrendingTool()
        r = t._run("agentic-ai", max_results=2)
        ok = len([x for x in r if "error" not in x]) > 0
        tests.append(("GitHub API", ok, f"{len(r)} results"))
    except Exception as e:
        tests.append(("GitHub API", False, str(e)[:80]))

    # Hacker News
    try:
        from tools.hackernews_tool import HackerNewsSearchTool
        t = HackerNewsSearchTool()
        r = t._run("agentic AI", max_results=2)
        ok = len([x for x in r if "error" not in x]) > 0
        tests.append(("Hacker News", ok, f"{len(r)} results"))
    except Exception as e:
        tests.append(("Hacker News", False, str(e)[:80]))

    # OpenAlex
    try:
        from tools.openalex_crossref_tool import OpenAlexSearchTool
        t = OpenAlexSearchTool()
        r = t._run("world model JEPA", max_results=2)
        ok = len([x for x in r if "error" not in x]) > 0
        tests.append(("OpenAlex", ok, f"{len(r)} results"))
    except Exception as e:
        tests.append(("OpenAlex", False, str(e)[:80]))

    # CrossRef
    try:
        from tools.openalex_crossref_tool import CrossRefSearchTool
        t = CrossRefSearchTool()
        r = t._run("geometric deep learning", max_results=2)
        ok = len([x for x in r if "error" not in x]) > 0
        tests.append(("CrossRef", ok, f"{len(r)} results"))
    except Exception as e:
        tests.append(("CrossRef", False, str(e)[:80]))

    # Print results
    result_table = Table(title="API Test Results")
    result_table.add_column("API", style="cyan")
    result_table.add_column("Status")
    result_table.add_column("Details")

    passed = 0
    for name, ok, detail in tests:
        status = "[green]PASS[/green]" if ok else f"[red]FAIL[/red]"
        if ok:
            passed += 1
        result_table.add_row(name, status, detail)

    console.print(result_table)
    console.print(f"\n[bold]{passed}/{len(tests)}[/bold] APIs working.")

    if passed >= 4:
        console.print("[green]System is ready for full runs![/green]")
    else:
        console.print("[yellow]Some APIs failed — check your internet connection.[/yellow]")

    return passed >= 4


@click.command()
@click.option("--mode", "-m", type=click.Choice(["full", "academic", "industrial", "vacancies", "social"]),
              default="full", help="Which agents to run")
@click.option("--adk", is_flag=True, help="Use Google ADK mode instead of CrewAI")
@click.option("--schedule", "-s", type=int, default=0, help="Schedule: run every N hours (0 = once)")
@click.option("--output", "-o", type=str, default=None, help="Custom output file path")
@click.option("--test", is_flag=True, help="Run connectivity test only")
@click.option("--status", is_flag=True, help="Show API configuration status")
def main(mode, adk, schedule, output, test, status):
    console.print(BANNER)

    if status:
        check_environment()
        return

    if test:
        run_test()
        return

    if adk:
        # Google ADK mode
        from crew.adk_integration import run_adk_mode
        console.print(Panel(
            f"[bold]Running in Google ADK mode[/bold]\nMode: {mode}",
            border_style="yellow"
        ))
        run_adk_mode(mode=mode)
        return

    # CrewAI mode
    from crew.main_crew import run_crew

    if schedule > 0:
        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)

        console.print(Panel(
            f"[bold]Scheduled Mode[/bold]\nRunning every {schedule} hours\nPress Ctrl+C to stop",
            border_style="green"
        ))

        while _running:
            console.print(f"\n[cyan]Scheduled run at {datetime.now().isoformat()}[/cyan]")
            try:
                output_file = run_crew(mode=mode, output_file=output)
                console.print(f"[green]Report: {output_file}[/green]")
            except Exception as e:
                console.print(f"[red]Run failed: {e}[/red]")

            # Wait for next cycle
            for _ in range(schedule * 3600):
                if not _running:
                    break
                time.sleep(1)
    else:
        # Single run
        console.print(Panel(
            f"[bold]Single Run[/bold]\nMode: {mode}\nAgents: CrewAI",
            border_style="blue"
        ))
        output_file = run_crew(mode=mode, output_file=output)
        console.print(f"\n[bold green]Done! Report saved to:[/bold green] {output_file}")


if __name__ == "__main__":
    main()