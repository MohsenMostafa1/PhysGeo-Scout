"""
Standalone API tool functions for Hugging Face Spaces.
Decoupled from CrewAI — uses only requests + arxiv + feedparser.
Each function returns a list of dicts ready for Gradio display.
"""
import time
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import arxiv
import requests
import feedparser


# ═══════════════════════════════════════════════════════════════════
# ARXIV — Free, no key
# ═══════════════════════════════════════════════════════════════════

def search_arxiv(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search arXiv for papers."""
    results = []
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        for paper in client.results(search):
            if paper.published and (datetime.now(paper.published.tzinfo) - paper.published) > timedelta(days=90):
                continue
            results.append({
                "source": "arXiv",
                "title": paper.title.strip(),
                "authors": ", ".join([a.name for a in paper.authors[:4]]),
                "abstract": paper.summary.strip()[:400],
                "categories": ", ".join(paper.categories[:5]),
                "published": paper.published.strftime("%Y-%m-%d") if paper.published else "",
                "pdf_url": paper.pdf_url,
                "url": paper.entry_id,
            })
    except Exception as e:
        results.append({"source": "arXiv", "title": f"Error: {e}", "error": True})
    return results


def arxiv_category_feed(categories: str, max_per_cat: int = 8) -> List[Dict[str, Any]]:
    """Fetch latest papers from arXiv categories via RSS."""
    all_results = []
    for cat in [c.strip() for c in categories.split(",")]:
        url = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results={max_per_cat}"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                published = entry.find("atom:published", ns)
                link = entry.find("atom:id", ns)
                authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
                all_results.append({
                    "source": f"arXiv [{cat}]",
                    "title": title.text.strip().replace("\n", " ") if title is not None else "",
                    "authors": ", ".join(authors[:4]),
                    "abstract": summary.text.strip()[:300] if summary is not None else "",
                    "published": published.text[:10] if published is not None else "",
                    "url": link.text if link is not None else "",
                })
        except Exception as e:
            all_results.append({"source": f"arXiv [{cat}]", "title": f"Error: {e}", "error": True})
        time.sleep(1)
    return all_results


# ═══════════════════════════════════════════════════════════════════
# SEMANTIC SCHOLAR — Free (rate limited without key)
# ═══════════════════════════════════════════════════════════════════

SS_BASE = "https://api.semanticscholar.org/graph/v1"


def search_semantic_scholar(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Semantic Scholar for papers with citation counts."""
    results = []
    try:
        fields = "title,authors,year,citationCount,influentialCitationCount,abstract,url,openAccessPdf,publicationVenue,tldr"
        resp = requests.get(
            f"{SS_BASE}/paper/search",
            params={"query": query, "limit": max_results, "fields": fields, "year": "2025-2026"},
            timeout=20,
        )
        if resp.status_code == 200:
            for p in resp.json().get("data", []):
                tldr = p.get("tldr", {})
                abstract = (tldr.get("text", "") or p.get("abstract", ""))[:400]
                results.append({
                    "source": "Semantic Scholar",
                    "title": p.get("title", ""),
                    "authors": ", ".join([a.get("name", "") for a in p.get("authors", [])[:4]]),
                    "year": p.get("year", ""),
                    "citations": p.get("citationCount", 0),
                    "influential": p.get("influentialCitationCount", 0),
                    "abstract": abstract,
                    "url": p.get("url", ""),
                    "pdf_url": (p.get("openAccessPdf") or {}).get("url", ""),
                    "venue": p.get("publicationVenue", ""),
                })
        else:
            results.append({"source": "Semantic Scholar", "title": f"API returned {resp.status_code}", "error": True})
    except Exception as e:
        results.append({"source": "Semantic Scholar", "title": f"Error: {e}", "error": True})
    time.sleep(1)
    return results


def track_author_papers(author_name: str, max_results: int = 8) -> List[Dict[str, Any]]:
    """Fetch recent papers by a specific author."""
    results = []
    try:
        resp = requests.get(
            f"{SS_BASE}/author/search",
            params={"query": author_name, "limit": 1, "fields": "authorId,paperCount,name"},
            timeout=15,
        )
        if resp.status_code != 200 or not resp.json().get("data"):
            return [{"source": "Semantic Scholar", "title": f"Author '{author_name}' not found", "error": True}]

        author_id = resp.json()["data"][0]["authorId"]
        fields = "title,authors,year,citationCount,abstract,url,openAccessPdf,publicationVenue"
        papers_resp = requests.get(
            f"{SS_BASE}/author/{author_id}/papers",
            params={"limit": max_results, "fields": fields, "year": "2025-2026"},
            timeout=20,
        )
        if papers_resp.status_code == 200:
            for p in papers_resp.json().get("data", []):
                results.append({
                    "source": f"Semantic Scholar [{author_name}]",
                    "title": p.get("title", ""),
                    "authors": ", ".join([a.get("name", "") for a in p.get("authors", [])[:4]]),
                    "year": p.get("year", ""),
                    "citations": p.get("citationCount", 0),
                    "abstract": (p.get("abstract") or "")[:400],
                    "url": p.get("url", ""),
                    "pdf_url": (p.get("openAccessPdf") or {}).get("url", ""),
                    "venue": p.get("publicationVenue", ""),
                })
    except Exception as e:
        results.append({"source": "Semantic Scholar", "title": f"Error: {e}", "error": True})
    time.sleep(1)
    return results


# ═══════════════════════════════════════════════════════════════════
# GITHUB — Free (60 req/hour)
# ═══════════════════════════════════════════════════════════════════

GH_HEADERS = {"Accept": "application/vnd.github.v3+json"}


def github_trending(topic: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Find trending GitHub repos for a topic."""
    results = []
    since = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    try:
        resp = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": f"{topic} created:>{since} stars:>5", "sort": "stars", "order": "desc", "per_page": max_results},
            headers=GH_HEADERS, timeout=15,
        )
        if resp.status_code == 200:
            for repo in resp.json().get("items", []):
                results.append({
                    "source": "GitHub",
                    "name": repo["full_name"],
                    "description": (repo.get("description") or "")[:250],
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language", ""),
                    "url": repo.get("html_url", ""),
                    "topics": ", ".join(repo.get("topics", [])[:6]),
                    "license": (repo.get("license") or {}).get("name", ""),
                })
    except Exception as e:
        results.append({"source": "GitHub", "title": f"Error: {e}", "error": True})
    time.sleep(1)
    return results


def github_releases(repos: str, max_per_repo: int = 2) -> List[Dict[str, Any]]:
    """Get latest releases from key repos."""
    all_results = []
    for repo_name in [r.strip() for r in repos.split(",")]:
        try:
            resp = requests.get(
                f"https://api.github.com/repos/{repo_name}/releases",
                params={"per_page": max_per_repo},
                headers=GH_HEADERS, timeout=10,
            )
            if resp.status_code == 200:
                for rel in resp.json():
                    all_results.append({
                        "source": f"GitHub Releases",
                        "title": f"{repo_name} — {rel.get('name', rel.get('tag_name', ''))}",
                        "tag": rel.get("tag_name", ""),
                        "body": (rel.get("body") or "")[:400],
                        "published": rel.get("published_at", "")[:10],
                        "url": rel.get("html_url", ""),
                    })
        except Exception as e:
            all_results.append({"source": "GitHub Releases", "title": f"{repo_name}: {e}", "error": True})
        time.sleep(0.5)
    return all_results


# ═══════════════════════════════════════════════════════════════════
# HACKER NEWS — Free, no key (via Algolia)
# ═══════════════════════════════════════════════════════════════════

def search_hackernews(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Hacker News for AI stories."""
    results = []
    try:
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": query, "tags": "story", "numericFilters": "points>3", "hitsPerPage": max_results},
            timeout=15,
        )
        if resp.status_code == 200:
            for hit in resp.json().get("hits", []):
                results.append({
                    "source": "Hacker News",
                    "title": hit.get("title", ""),
                    "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                    "points": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                    "author": hit.get("author", ""),
                    "date": hit.get("created_at", "")[:10],
                })
    except Exception as e:
        results.append({"source": "Hacker News", "title": f"Error: {e}", "error": True})
    return results


def hn_who_is_hiring(max_results: int = 30) -> List[Dict[str, Any]]:
    """Fetch HN 'Who is Hiring' threads filtered for AI/ML jobs."""
    results = []
    ai_kw = ["ai", "ml", "machine learning", "deep learning", "computer vision",
             "llm", "nlp", "robotics", "mlops", "data scientist", "research scientist",
             "agentic", "generative ai", "pytorch", "tensorflow", "engineer"]
    try:
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": "Who is hiring", "tags": "story", "hitsPerPage": 1},
            timeout=15,
        )
        if resp.status_code != 200:
            return [{"source": "HN Hiring", "title": "Fetch failed", "error": True}]

        for hit in resp.json().get("hits", []):
            story_id = hit.get("objectID")
            title = hit.get("title", "")
            comments_resp = requests.get(
                f"https://hn.algolia.com/api/v1/search",
                params={"tags": f"comment,story_{story_id}", "hitsPerPage": 200},
                timeout=20,
            )
            if comments_resp.status_code != 200:
                continue
            for comment in comments_resp.json().get("hits", []):
                text = comment.get("comment_text", "").lower()
                if any(kw in text for kw in ai_kw):
                    results.append({
                        "source": f"HN Who is Hiring [{title}]",
                        "title": text[:200] + "...",
                        "url": f"https://news.ycombinator.com/item?id={comment.get('objectID')}",
                        "author": comment.get("author", ""),
                    })
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break
    except Exception as e:
        results.append({"source": "HN Hiring", "title": f"Error: {e}", "error": True})
    return results


# ═══════════════════════════════════════════════════════════════════
# OPENALEX — Free, no key
# ═══════════════════════════════════════════════════════════════════

def search_openalex(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search OpenAlex for papers."""
    results = []
    try:
        resp = requests.get(
            "https://api.openalex.org/works",
            params={"search": query, "per_page": max_results, "sort": "publication_date:desc",
                    "filter": "from_publication_date:2025-01-01"},
            timeout=20,
        )
        if resp.status_code == 200:
            for work in resp.json().get("results", []):
                authors = []
                for auth in work.get("authorships", [])[:4]:
                    a = auth.get("author", {})
                    insts = auth.get("institutions", [])
                    inst_str = f" ({insts[0].get('display_name', '')})" if insts else ""
                    authors.append(a.get("display_name", "") + inst_str)
                concepts = [c.get("display_name", "") for c in work.get("concepts", [])[:4]]
                results.append({
                    "source": "OpenAlex",
                    "title": work.get("title", ""),
                    "authors": ", ".join(authors),
                    "date": work.get("publication_date", ""),
                    "citations": work.get("cited_by_count", 0),
                    "concepts": ", ".join(concepts),
                    "doi": work.get("doi", ""),
                    "venue": (work.get("primary_location", {}) or {}).get("source", {}).get("display_name", ""),
                    "open_access": work.get("open_access", {}).get("is_oa", False),
                })
    except Exception as e:
        results.append({"source": "OpenAlex", "title": f"Error: {e}", "error": True})
    time.sleep(0.5)
    return results


def openalex_institution_papers(institution: str, max_results: int = 8) -> List[Dict[str, Any]]:
    """Get recent papers from a specific institution."""
    results = []
    try:
        inst_resp = requests.get(
            "https://api.openalex.org/institutions",
            params={"search": institution, "per_page": 1},
            timeout=15,
        )
        if inst_resp.status_code != 200 or not inst_resp.json().get("results"):
            return [{"source": "OpenAlex", "title": f"Institution '{institution}' not found", "error": True}]

        inst_id = inst_resp.json()["results"][0]["id"]
        inst_name = inst_resp.json()["results"][0].get("display_name", institution)

        papers_resp = requests.get(
            "https://api.openalex.org/works",
            params={"filter": f"authorships.institutions.id:{inst_id},from_publication_date:2025-01-01",
                    "sort": "cited_by_count:desc", "per_page": max_results},
            timeout=20,
        )
        if papers_resp.status_code == 200:
            for work in papers_resp.json().get("results", []):
                authors = [a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])[:4]]
                results.append({
                    "source": f"OpenAlex [{inst_name}]",
                    "title": work.get("title", ""),
                    "authors": ", ".join(authors),
                    "date": work.get("publication_date", ""),
                    "citations": work.get("cited_by_count", 0),
                    "doi": work.get("doi", ""),
                    "concepts": ", ".join([c.get("display_name", "") for c in work.get("concepts", [])[:4]]),
                })
    except Exception as e:
        results.append({"source": "OpenAlex", "title": f"Error: {e}", "error": True})
    time.sleep(0.5)
    return results


# ═══════════════════════════════════════════════════════════════════
# CROSSREF — Free, no key
# ═══════════════════════════════════════════════════════════════════

def search_crossref(query: str, max_results: int = 8) -> List[Dict[str, Any]]:
    """Search CrossRef for journal/conference papers."""
    results = []
    try:
        resp = requests.get(
            "https://api.crossref.org/works",
            params={"query": query, "rows": max_results, "sort": "published", "order": "desc",
                    "filter": "from-pub-date:2025-01-01"},
            timeout=20,
        )
        if resp.status_code == 200:
            for item in resp.json().get("message", {}).get("items", []):
                authors = [f"{a.get('given','')} {a.get('family','')}".strip() for a in item.get("author", [])[:4]]
                pub_date = item.get("published-print", item.get("published-online", {})).get("date-parts", [[]])[0]
                results.append({
                    "source": "CrossRef",
                    "title": item.get("title", [""])[0] if item.get("title") else "",
                    "authors": ", ".join(authors),
                    "date": "-".join(str(d) for d in pub_date) if pub_date else "",
                    "doi": item.get("DOI", ""),
                    "type": item.get("type", ""),
                    "venue": item.get("container-title", [""])[0] if item.get("container-title") else "",
                    "url": f"https://doi.org/{item.get('DOI', '')}" if item.get("DOI") else "",
                    "publisher": item.get("publisher", ""),
                })
    except Exception as e:
        results.append({"source": "CrossRef", "title": f"Error: {e}", "error": True})
    time.sleep(0.5)
    return results


# ═══════════════════════════════════════════════════════════════════
# PROFILE MATCH SCORER
# ═══════════════════════════════════════════════════════════════════

PROFILE_SKILLS = {
    "languages": {"python", "c++", "sql", "pyspark"},
    "ml_dl": {"pytorch", "tensorflow", "hugging face", "scikit-learn", "xgboost", "yolo", "opencv"},
    "genai_llm": {"llm", "rag", "langchain", "falcon", "deepseek", "llama", "qwen", "mistral", "colbert", "rlhf"},
    "cv": {"computer vision", "point cloud", "lidar", "object detection", "image segmentation", "mask2former", "multi-view geometry"},
    "mlops": {"mlops", "kubernetes", "docker", "mlflow", "kubeflow", "kafka", "airflow", "fastapi", "tensorrt", "onnx", "kserve"},
    "research": {"geometric deep learning", "physics-informed", "world model", "robotics", "research", "uncertainty quantification", "bayesian", "physical ai"},
    "cloud": {"aws", "gcp", "vertex ai", "sagemaker", "prometheus", "grafana"},
    "iot_drone": {"iot", "drone", "uav", "edge ai", "tinyml", "federated learning", "jetson", "raspberry pi", "ndvi", "satellite", "anomaly detection", "real-time"},
    "data_infra": {"data pipeline", "spark", "hadoop", "kafka", "gpu cluster", "distributed training", "vector database", "dagster", "data engineering", "streaming"},
}


def score_vacancy(text: str) -> tuple:
    """Score a vacancy text against Mohsen's profile. Returns (score, matched_skills)."""
    text_lower = text.lower()
    score = 0
    matched = []
    for group, skills in PROFILE_SKILLS.items():
        for skill in skills:
            if skill.lower() in text_lower:
                score += 2
                matched.append(skill)
    if any(w in text_lower for w in ["lead", "senior", "principal", "head", "staff"]):
        score += 5
        matched.append("senior/lead")
    if "remote" in text_lower:
        score += 3
        matched.append("remote")
    if "research" in text_lower:
        score += 4
        matched.append("research")
    return score, matched
