"""
Semantic Scholar API Tool — Free, optional API key for higher limits.
Provides citation data, related papers, author profiles.
"""
import time
from typing import List, Dict, Any

import requests
from crewai.tools import BaseTool
from config import SEMANTIC_SCHOLAR_API_KEY


BASE_URL = "https://api.semanticscholar.org/graph/v1"
HEADERS = {}
if SEMANTIC_SCHOLAR_API_KEY:
    HEADERS["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY


class SemanticScholarSearchTool(BaseTool):
    name: str = "semantic_scholar_search"
    description: str = (
        "Searches Semantic Scholar for academic papers with citation counts, "
        "influential citations, and related papers. Better for finding impactful "
        "and well-cited research. Input: a search query string."
    )

    def _run(self, query: str, max_results: int = 15) -> List[Dict[str, Any]]:
        fields = "title,authors,year,citationCount,influentialCitationCount,abstract,url,openAccessPdf,publicationVenue,tldr"
        results = []
        try:
            params = {
                "query": query,
                "limit": min(max_results, 100),
                "fields": fields,
                "year": "2025-2026",
                "openAccessPdf": "true",
            }
            resp = requests.get(f"{BASE_URL}/paper/search", params=params, headers=HEADERS, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                for p in data.get("data", []):
                    tldr = p.get("tldr", {})
                    results.append({
                        "source": "Semantic Scholar",
                        "title": p.get("title", ""),
                        "authors": [a.get("name", "") for a in p.get("authors", [])[:5]],
                        "year": p.get("year", ""),
                        "citation_count": p.get("citationCount", 0),
                        "influential_citations": p.get("influentialCitationCount", 0),
                        "abstract": (tldr.get("text", "") or p.get("abstract", ""))[:500],
                        "url": p.get("url", ""),
                        "pdf_url": (p.get("openAccessPdf") or {}).get("url", ""),
                        "venue": p.get("publicationVenue", ""),
                    })
            else:
                results.append({"error": f"Semantic Scholar API returned {resp.status_code}", "source": "Semantic Scholar"})
        except Exception as e:
            results.append({"error": f"Semantic Scholar search failed: {str(e)}", "source": "Semantic Scholar"})

        time.sleep(1)
        return results


class SemanticScholarAuthorTool(BaseTool):
    """Fetch papers by specific authors (e.g., Yann LeCun)."""
    name: str = "semantic_scholar_author"
    description: str = (
        "Fetches recent papers by a specific author. Use for tracking Yann LeCun, "
        "or other key researchers. Input: author name string."
    )

    def _run(self, author_name: str, max_results: int = 10) -> List[Dict[str, Any]]:
        fields = "title,authors,year,citationCount,abstract,url,openAccessPdf,publicationVenue"
        results = []
        try:
            # First search for the author
            resp = requests.get(
                f"{BASE_URL}/author/search",
                params={"query": author_name, "limit": 1, "fields": "authorId,paperCount,name"},
                headers=HEADERS, timeout=15,
            )
            if resp.status_code != 200 or not resp.json().get("data"):
                return [{"error": f"Author '{author_name}' not found", "source": "Semantic Scholar"}]

            author_id = resp.json()["data"][0]["authorId"]

            # Then get their recent papers
            papers_resp = requests.get(
                f"{BASE_URL}/author/{author_id}/papers",
                params={"limit": max_results, "fields": fields, "year": "2025-2026"},
                headers=HEADERS, timeout=20,
            )
            if papers_resp.status_code == 200:
                for p in papers_resp.json().get("data", []):
                    results.append({
                        "source": f"Semantic Scholar [{author_name}]",
                        "title": p.get("title", ""),
                        "authors": [a.get("name", "") for a in p.get("authors", [])[:5]],
                        "year": p.get("year", ""),
                        "citation_count": p.get("citationCount", 0),
                        "abstract": p.get("abstract", "")[:500] if p.get("abstract") else "",
                        "url": p.get("url", ""),
                        "pdf_url": (p.get("openAccessPdf") or {}).get("url", ""),
                        "venue": p.get("publicationVenue", ""),
                    })
        except Exception as e:
            results.append({"error": f"Author search failed: {str(e)}", "source": "Semantic Scholar"})

        time.sleep(1)
        return results


class SemanticScholarReferenceTool(BaseTool):
    """Find papers that reference or are referenced by a given paper."""
    name: str = "semantic_scholar_references"
    description: str = (
        "Finds papers related to a given paper URL or arXiv ID via citations. "
        "Input: paper URL or arXiv ID."
    )

    def _run(self, paper_url: str, max_results: int = 10) -> List[Dict[str, Any]]:
        fields = "title,authors,year,citationCount,abstract,url"
        results = []
        try:
            search_resp = requests.get(
                f"{BASE_URL}/paper/search",
                params={"query": paper_url, "limit": 1, "fields": "paperId,title"},
                headers=HEADERS, timeout=15,
            )
            if search_resp.status_code != 200:
                return [{"error": "Paper lookup failed", "source": "Semantic Scholar"}]

            paper_id = search_resp.json().get("data", [{}])[0].get("paperId")
            if not paper_id:
                return [{"error": "Paper not found", "source": "Semantic Scholar"}]

            cite_resp = requests.get(
                f"{BASE_URL}/paper/{paper_id}/citations",
                params={"limit": max_results, "fields": fields},
                headers=HEADERS, timeout=20,
            )
            if cite_resp.status_code == 200:
                for c in cite_resp.json().get("data", []):
                    p = c.get("citingPaper", {})
                    results.append({
                        "source": "Semantic Scholar [citations]",
                        "title": p.get("title", ""),
                        "year": p.get("year", ""),
                        "citation_count": p.get("citationCount", 0),
                        "url": p.get("url", ""),
                    })
        except Exception as e:
            results.append({"error": f"Reference lookup failed: {str(e)}", "source": "Semantic Scholar"})

        return results
