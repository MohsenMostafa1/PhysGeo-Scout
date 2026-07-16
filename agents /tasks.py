"""
CrewAI Tasks — Each task is assigned to a specific agent with clear expected output.
Tasks are designed to produce structured, actionable results.
"""
import json
from crewai import Task
from config import (
    ACADEMIC_QUERIES, INDUSTRIAL_QUERIES, VACANCY_QUERIES,
    SUBREDDITS_TO_MONITOR, HACKER_NEWS_TOPICS, MAX_RESULTS_PER_SOURCE,
)


def build_academic_tasks(tools_dict):
    """Build tasks for the Academic Research Agent."""
    tasks = []

    # Task 1: Search arXiv for Physical AI, World Models, Robotics papers
    tasks.append(Task(
        description=(
            "Search arXiv for the latest papers on Physical AI, World Models, "
            "JEPA architectures, geometric deep learning, and robotics AI. "
            "Use these queries one by one:\n"
            "{queries}\n\n"
            "For each query, use the arxiv_search tool with max_results={max_results}. "
            "Compile all results and return a structured list."
        ).format(
            queries="\n".join(f"  - {q}" for q in ACADEMIC_QUERIES["physical_ai"][:5]),
            max_results=MAX_RESULTS_PER_SOURCE,
        ),
        agent=tools_dict["academic_agent"],
        expected_output="A structured list of the most relevant academic papers from arXiv, "
                        "each with title, authors, abstract, PDF link, and relevance reason.",
        tools=[tools_dict["arxiv_search"], tools_dict["arxiv_rss"]],
    ))

    # Task 2: Track specific researchers via Semantic Scholar
    tasks.append(Task(
        description=(
            "Track recent papers from these key researchers using the semantic_scholar_author tool:\n"
            "1. Yann LeCun — focus on world models, JEPA, embodied AI\n"
            "2. Yann LeCun's collaborators at NYU/Meta FAIR\n\n"
            "Also use semantic_scholar_search for these topics:\n"
            "{topics}\n\n"
            "Return papers with citation counts and relevance notes."
        ).format(
            topics="\n".join(f"  - {q}" for q in ACADEMIC_QUERIES["physical_ai"][5:]),
        ),
        agent=tools_dict["academic_agent"],
        expected_output="A structured list of papers from key researchers (especially Yann LeCun, NYU, Meta FAIR) "
                        "with citation metrics and relevance to Physical & Geometric AI research.",
        tools=[tools_dict["semantic_scholar_search"], tools_dict["semantic_scholar_author"]],
    ))

    # Task 3: Track papers from key institutions via OpenAlex
    tasks.append(Task(
        description=(
            "Search OpenAlex for recent papers from these top AI research labs:\n"
            "{labs}\n\n"
            "Use the openalex_institution tool for each. Also search openalex_search "
            "for 'robotics foundation models' and 'embodied AI world models'.\n"
            "Return papers with institution name, citation count, and relevance."
        ).format(
            labs="\n".join(f"  - {lab}" for lab in ACADEMIC_QUERIES["key_labs"]),
        ),
        agent=tools_dict["academic_agent"],
        expected_output="A structured list of papers from top AI labs (NYU, Meta FAIR, DeepMind, MIT, Stanford, ETH, CMU) "
                        "with institution attribution, citation counts, and relevance scores.",
        tools=[tools_dict["openalex_search"], tools_dict["openalex_institution"]],
    ))

    return tasks


def build_industrial_tasks(tools_dict):
    """Build tasks for the Industrial Research Agent."""
    tasks = []

    # Task 1: Track LLM & Agentic AI frameworks
    tasks.append(Task(
        description=(
            "Search for the latest industrial developments in LLMs, Agentic AI, and AI frameworks.\n\n"
            "1. Use github_trending for these topics: 'agentic-ai', 'llm-agent', 'mlops', 'fine-tuning-llm'\n"
            "2. Use github_repo_search for: 'CrewAI agent', 'LangGraph agent', 'Google ADK agent', 'world model JEPA implementation'\n"
            "3. Use hackernews_search for: 'agentic AI framework 2025', 'LLM optimization technique', 'MLOps tool'\n\n"
            "Return findings with GitHub stars, description, and practical relevance."
        ),
        agent=tools_dict["industrial_agent"],
        expected_output="A structured list of the latest AI frameworks, tools, and libraries "
                        "with GitHub metrics, descriptions, and relevance to production AI systems.",
        tools=[
            tools_dict["github_trending"], tools_dict["github_repo_search"],
            tools_dict["hackernews_search"],
        ],
    ))

    # Task 2: Track NVIDIA, MLOps, fine-tuning
    tasks.append(Task(
        description=(
            "Search for the latest in NVIDIA AI, MLOps, and fine-tuning:\n\n"
            "1. Use github_releases for: 'huggingface/transformers', 'pytorch/pytorch', 'vllm-project/vllm', 'nvidia/cuda-samples'\n"
            "2. Use hackernews_search for: 'NVIDIA AI framework', 'fine-tuning LoRA QLoRA', 'TensorRT optimization', 'MLOps best practices'\n"
            "3. Use semantic_scholar_search for: 'MLOps production deployment', 'LLM fine-tuning efficiency'\n\n"
            "Return all findings with release details, practical applications, and relevance."
        ),
        agent=tools_dict["industrial_agent"],
        expected_output="A structured list of NVIDIA tools, MLOps practices, fine-tuning techniques, "
                        "and framework releases with version numbers, dates, and practical relevance.",
        tools=[
            tools_dict["github_releases"], tools_dict["hackernews_search"],
            tools_dict["semantic_scholar_search"],
        ],
    ))

    return tasks


def build_social_media_tasks(tools_dict):
    """Build tasks for the Social Media Monitor Agent."""
    tasks = []

    tasks.append(Task(
        description=(
            "Monitor AI communities for trending discussions and new releases:\n\n"
            "1. Use reddit_subreddit_monitor for: '{subreddits}'\n"
            "2. Use hackernews_search for these trending topics:\n{hn_topics}\n"
            "3. Use reddit_search for: 'Yann LeCun world model', 'agentic AI framework new', 'physical AI robotics'\n\n"
            "Identify the top 20 most discussed/engaged items across all sources. "
            "Return with engagement metrics (upvotes, comments) and relevance notes."
        ).format(
            subreddits=",".join(SUBREDDITS_TO_MONITOR[:8]),
            hn_topics="\n".join(f"  - {t}" for t in HACKER_NEWS_TOPICS),
        ),
        agent=tools_dict["social_media_agent"],
        expected_output="A structured list of trending AI discussions, new releases, and community highlights "
                        "from Reddit and Hacker News with engagement metrics.",
        tools=[
            tools_dict["reddit_monitor"], tools_dict["reddit_search"],
            tools_dict["hackernews_search"],
        ],
    ))

    return tasks


def build_vacancy_tasks(tools_dict):
    """Build tasks for the Vacancy Scout Agent."""
    tasks = []

    tasks.append(Task(
        description=(
            "Find AI/ML job vacancies matching Mohsen Mostafa's profile:\n\n"
            "1. Use job_aggregator with roles: '{roles}'\n"
            "2. Use hackernews_who_is_hiring to get the latest HN hiring thread\n"
            "3. Use reddit_vacancy_search with: '{roles}'\n\n"
            "Then use profile_match_scorer to rank all collected jobs.\n\n"
            "Return the top 20 highest-matching vacancies with match scores and reasoning."
        ).format(
            roles=",".join(VACANCY_QUERIES["roles"][:6]),
        ),
        agent=tools_dict["vacancy_agent"],
        expected_output="A ranked list of AI/ML job vacancies scored against Mohsen's profile, "
                        "with match scores, company hints, locations, and application links.",
        tools=[
            tools_dict["job_aggregator"], tools_dict["hn_hiring"],
            tools_dict["reddit_vacancy"], tools_dict["profile_scorer"],
        ],
    ))

    return tasks


def build_synthesis_task(tools_dict):
    """Build the final synthesis task."""
    return Task(
        description=(
            "Synthesize ALL findings from the other agents into a comprehensive, "
            "actionable research intelligence report.\n\n"
            "Your report MUST follow this structure:\n\n"
            "## 1. EXECUTIVE SUMMARY\n"
            "Top 5-10 highlights from this intelligence cycle.\n\n"
            "## 2. TOP ACADEMIC PAPERS (ranked by relevance)\n"
            "For each paper: title, authors, source, relevance to Physical & Geometric AI, "
            "link, and why Mohsen should read it.\n\n"
            "## 3. INDUSTRIAL DEVELOPMENTS\n"
            "New frameworks, tools, releases, and techniques with practical value.\n\n"
            "## 4. TRENDING REPOS & FRAMEWORKS\n"
            "GitHub repos with stars, descriptions, and potential use cases.\n\n"
            "## 5. COMMUNITY HIGHLIGHTS\n"
            "Key discussions, opinions, and trends from Reddit and HN.\n\n"
            "## 6. VACANCY ALERTS (ranked by match score)\n"
            "Top job matches with scores, company, role, and application links.\n\n"
            "## 7. RECOMMENDED ACTIONS\n"
            "Papers to read, tools to try, jobs to apply to, people to follow.\n\n"
            "After generating the report, also use discord_notify to send a summary alert."
        ),
        agent=tools_dict["synthesis_agent"],
        expected_output="A comprehensive, well-structured research intelligence report in Markdown format "
                        "covering academic papers, industrial tools, community trends, and job vacancies, "
                        "all ranked by relevance to Mohsen Mostafa's research and career.",
        tools=[tools_dict["discord_notify"]],
    )
