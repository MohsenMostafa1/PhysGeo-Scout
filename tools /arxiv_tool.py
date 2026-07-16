"""
arXiv Search Tool — Free API, no key required.
Fetches papers, preprints matching research queries.
"""
import time
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import arxiv
import requests
from crewai.tools import BaseTool


class ArxivSearchTool(BaseTool):
    name: str = "arxiv_search"
    description: str = (
        "Searches arXiv for research papers and preprints. "
        "Use for finding the latest papers on LLMs, computer vision, robotics, "
        "physical AI, MLOps, Agentic AI, fine-tuning, optimization, and more. "
        "Returns paper titles, authors, abstracts, categories, and PDF links. "
        "Input: a search query string."
    )

    def _run(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search arXiv and return structured paper data."""
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
                # Filter to recent papers (last 90 days) for relevance
                if paper.published and (datetime.now(paper.published.tzinfo) - paper.published) > timedelta(days=90):
                    continue
                results.append({
                    "source": "arXiv",
                    "title": paper.title.strip(),
                    "authors": [a.name for a in paper.authors],
                    "abstract": paper.summary.strip()[:500],
                    "categories": paper.categories,
                    "published": paper.published.isoformat() if paper.published else "",
                    "pdf_url": paper.pdf_url,
                    "entry_id": paper.entry_id,
                    "doi": paper.doi,
                })
        except Exception as e:
            return [{"error": f"arXiv search failed: {str(e)}", "source": "arXiv"}]

        time.sleep(0.5)  # Be polite to arXiv API
        return results


class ArxivRSSFeedTool(BaseTool):
    """Fetch latest papers from arXiv category RSS feeds (e.g., cs.CV, cs.AI, cs.RO)."""
    name: str = "arxiv_rss_feed"
    description: str = (
        "Fetches the latest papers from specific arXiv categories via RSS. "
        "Useful for monitoring cs.CV, cs.AI, cs.RO, cs.LG, cs.CL. "
        "Input: comma-separated list of arXiv categories (e.g. 'cs.CV,cs.AI,cs.RO')"
    )

    def _run(self, categories: str, max_per_category: int = 10) -> List[Dict[str, Any]]:
        all_results = []
        cat_list = [c.strip() for c in categories.split(",")]

        for cat in cat_list:
            url = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results={max_per_category}"
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
                        "source": f"arXiv RSS [{cat}]",
                        "title": title.text.strip().replace("\n", " ") if title is not None else "",
                        "authors": authors,
                        "abstract": summary.text.strip()[:400] if summary is not None else "",
                        "published": published.text if published is not None else "",
                        "pdf_url": link.text if link is not None else "",
                        "category": cat,
                    })
            except Exception as e:
                all_results.append({"error": f"arXiv RSS for {cat} failed: {str(e)}", "source": "arXiv RSS"})

            time.sleep(1)

        return all_results
