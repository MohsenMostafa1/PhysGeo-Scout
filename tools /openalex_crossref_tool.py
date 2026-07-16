"""
OpenAlex & CrossRef Tools — Free academic APIs, no keys required.
OpenAlex: comprehensive open scholarly metadata (papers, authors, institutions, concepts).
CrossRef: DOI metadata, funding info, and reference linking.
"""
import time
from typing import List, Dict, Any

import requests
from crewai.tools import BaseTool


OPENALEX_API = "https://api.openalex.org"
CROSSREF_API = "https://api.crossref.org"


class OpenAlexSearchTool(BaseTool):
    """Search OpenAlex for papers, authors, and institutions."""
    name: str = "openalex_search"
    description: str = (
        "Searches OpenAlex for scholarly papers with rich metadata. "
        "Can filter by institution (NYU, Meta FAIR), author, concepts. "
        "Input: search query string."
    )

    def _run(self, query: str, max_results: int = 15) -> List[Dict[str, Any]]:
        results = []
        try:
            params = {
                "search": query,
                "per_page": max_results,
                "sort": "publication_date:desc",
                "filter": "from_publication_date:2025-01-01",
            }
            resp = requests.get(f"{OPENALEX_API}/works", params=params, timeout=20)
            if resp.status_code == 200:
                for work in resp.json().get("results", []):
                    authors = []
                    for auth in work.get("authorships", []):
                        a = auth.get("author", {})
                        authors.append(a.get("display_name", ""))
                        inst = auth.get("institutions", [])
                        if inst:
                            authors[-1] += f" ({inst[0].get('display_name', '')})"

                    concepts = [c.get("display_name", "") for c in work.get("concepts", [])[:5]]

                    results.append({
                        "source": "OpenAlex",
                        "title": work.get("title", ""),
                        "authors": authors[:5],
                        "publication_date": work.get("publication_date", ""),
                        "concepts": concepts,
                        "type": work.get("type", ""),
                        "cited_by_count": work.get("cited_by_count", 0),
                        "doi": work.get("doi", ""),
                        "open_access": work.get("open_access", {}).get("is_oa", False),
                        "url": work.get("doi", "").replace("https://doi.org/", "https://api.openalex.org/works/doi:") if work.get("doi") else "",
                        "abstract_inverted": work.get("abstract_inverted_index"),
                        "host_venue": (work.get("primary_location", {}) or {}).get("source", {}).get("display_name", ""),
                    })
        except Exception as e:
            results.append({"error": f"OpenAlex search failed: {str(e)}", "source": "OpenAlex"})

        time.sleep(0.5)
        return results


class OpenAlexInstitutionTool(BaseTool):
    """Search for papers from specific institutions (NYU, Meta FAIR, DeepMind, etc.)."""
    name: str = "openalex_institution"
    description: str = (
        "Fetches recent papers from a specific research institution. "
        "Use for tracking NYU, Meta FAIR, DeepMind, MIT CSAIL, Stanford Vision Lab. "
        "Input: institution name (e.g. 'New York University' or 'Meta AI')"
    )

    def _run(self, institution: str, max_results: int = 15) -> List[Dict[str, Any]]:
        results = []
        try:
            # First find the institution ID
            inst_resp = requests.get(
                f"{OPENALEX_API}/institutions",
                params={"search": institution, "per_page": 1},
                timeout=15,
            )
            if inst_resp.status_code != 200:
                return [{"error": f"Institution '{institution}' not found", "source": "OpenAlex"}]

            inst_data = inst_resp.json().get("results", [])
            if not inst_data:
                return [{"error": f"Institution '{institution}' not found", "source": "OpenAlex"}]

            inst_id = inst_data[0]["id"]
            inst_name = inst_data[0].get("display_name", institution)

            # Now get papers from this institution
            papers_resp = requests.get(
                f"{OPENALEX_API}/works",
                params={
                    "filter": f"authorships.institutions.id:{inst_id},from_publication_date:2025-01-01",
                    "sort": "cited_by_count:desc",
                    "per_page": max_results,
                },
                timeout=20,
            )
            if papers_resp.status_code == 200:
                for work in papers_resp.json().get("results", []):
                    authors = [a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])[:5]]
                    results.append({
                        "source": f"OpenAlex [{inst_name}]",
                        "title": work.get("title", ""),
                        "authors": authors,
                        "publication_date": work.get("publication_date", ""),
                        "cited_by_count": work.get("cited_by_count", 0),
                        "doi": work.get("doi", ""),
                        "concepts": [c.get("display_name", "") for c in work.get("concepts", [])[:5]],
                        "type": work.get("type", ""),
                    })
        except Exception as e:
            results.append({"error": f"Institution search failed: {str(e)}", "source": "OpenAlex"})

        time.sleep(0.5)
        return results


class CrossRefSearchTool(BaseTool):
    """Search CrossRef for DOI metadata and recent publications."""
    name: str = "crossref_search"
    description: str = (
        "Searches CrossRef for academic publications with DOI metadata. "
        "Good for finding journal articles, conference papers. "
        "Input: search query string."
    )

    def _run(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        results = []
        try:
            resp = requests.get(
                f"{CROSSREF_API}/works",
                params={
                    "query": query,
                    "rows": max_results,
                    "sort": "published",
                    "order": "desc",
                    "filter": "from-pub-date:2025-01-01",
                },
                timeout=20,
            )
            if resp.status_code == 200:
                for item in resp.json().get("message", {}).get("items", []):
                    authors = [
                        f"{a.get('given', '')} {a.get('family', '')}".strip()
                        for a in item.get("author", [])[:5]
                    ]
                    results.append({
                        "source": "CrossRef",
                        "title": item.get("title", [""])[0] if item.get("title") else "",
                        "authors": authors,
                        "published": item.get("published-print", item.get("published-online", {})).get("date-parts", [[]])[0] if item.get("published-print") or item.get("published-online") else [],
                        "doi": item.get("DOI", ""),
                        "type": item.get("type", ""),
                        "container_title": item.get("container-title", [""])[0] if item.get("container-title") else "",
                        "url": f"https://doi.org/{item.get('DOI', '')}" if item.get("DOI") else "",
                        "issn": item.get("ISSN", []),
                        "publisher": item.get("publisher", ""),
                    })
        except Exception as e:
            results.append({"error": f"CrossRef search failed: {str(e)}", "source": "CrossRef"})

        time.sleep(0.5)
        return results
