"""
Vacancy / Job Aggregation Tools — Fetches from multiple free sources.
Includes HN Who is Hiring, Reddit jobs, and generic web search.
"""
import json
import re
import time
from typing import List, Dict, Any

import requests
from crewai.tools import BaseTool


class JobAggregatorTool(BaseTool):
    """
    Aggregates AI/ML job vacancies from multiple free sources:
    - Hacker News Who is Hiring (via Algolia)
    - Reddit job posts
    - AI-specific job boards (via web scraping where possible)
    """
    name: str = "job_aggregator"
    description: str = (
        "Aggregates AI/ML/CV job vacancies from Hacker News, Reddit, and web sources. "
        "Input: comma-separated role keywords (e.g. 'AI Research Engineer,ML Ops,Computer Vision')"
    )

    def _run(self, role_keywords: str, max_results: int = 40) -> List[Dict[str, Any]]:
        all_jobs = []
        keywords = [k.strip() for k in role_keywords.split(",")]

        # 1. Hacker News — search for job posts
        try:
            for kw in keywords[:3]:
                resp = requests.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={
                        "query": f"{kw} hiring OR jobs OR vacancy OR position",
                        "tags": "story",
                        "hitsPerPage": 10,
                        "numericFilters": "points>3",
                    },
                    timeout=15,
                )
                if resp.status_code == 200:
                    for hit in resp.json().get("hits", []):
                        all_jobs.append({
                            "source": "Hacker News",
                            "title": hit.get("title", ""),
                            "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                            "points": hit.get("points", 0),
                            "company_hint": self._extract_company(hit.get("title", "")),
                            "location_hint": self._extract_location(hit.get("title", "")),
                            "remote": "remote" in hit.get("title", "").lower(),
                        })
                time.sleep(0.5)
        except Exception:
            pass

        # 2. AI-specific job RSS feeds
        ai_job_feeds = [
            ("https://www.indeed.com/rss?q=AI+Research+Engineer&l=Remote", "Indeed RSS"),
            ("https://www.indeed.com/rss?q=Computer+Vision+Engineer&l=Remote", "Indeed RSS"),
            ("https://www.indeed.com/rss?q=MLOps+Engineer&l=Remote", "Indeed RSS"),
        ]
        for feed_url, source_name in ai_job_feeds:
            try:
                import feedparser
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    all_jobs.append({
                        "source": source_name,
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "company_hint": self._extract_company(entry.get("title", "")),
                        "summary": entry.get("summary", "")[:300],
                    })
                time.sleep(1)
            except Exception:
                pass

        # 3. Generic web search for AI jobs (via public APIs)
        try:
            for kw in keywords[:2]:
                resp = requests.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={
                        "query": f"{kw} remote hiring 2025 2026",
                        "tags": "story",
                        "hitsPerPage": 5,
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    for hit in resp.json().get("hits", []):
                        all_jobs.append({
                            "source": "Web Search (HN)",
                            "title": hit.get("title", ""),
                            "url": hit.get("url", ""),
                            "company_hint": self._extract_company(hit.get("title", "")),
                            "remote": "remote" in hit.get("title", "").lower(),
                        })
                time.sleep(0.5)
        except Exception:
            pass

        # Deduplicate by URL
        seen = set()
        unique = []
        for job in all_jobs:
            url = job.get("url", "")
            if url and url not in seen:
                seen.add(url)
                unique.append(job)

        return unique[:max_results]

    @staticmethod
    def _extract_company(text: str) -> str:
        """Heuristic: extract likely company name from job title."""
        patterns = [
            r'(?:is hiring|is looking for|at )\s*([A-Z][A-Za-z0-9&\s]+)',
            r'([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+)*)\s*[-–]',
            r'^(.+?)\s+(?:is|hiring|looking)',
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()[:100]
        return ""


class ProfileMatchScorerTool(BaseTool):
    """
    Scores job vacancies against the user's profile (resume/CV).
    Uses keyword matching and skill overlap.
    """
    name: str = "profile_match_scorer"
    description: str = (
        "Scores a list of job vacancies against the user's resume profile. "
        "Returns jobs ranked by match score. Input: JSON string of jobs."
    )

    # Mohsen's key skills extracted from resume (module-level constant)
    PROFILE_SKILLS: dict = {
        "languages": {"python", "c++", "sql", "pyspark"},
        "ml_dl": {"pytorch", "tensorflow", "hugging face", "scikit-learn", "xgboost", "yolo", "opencv"},
        "genai_llm": {"llm", "rag", "langchain", "falcon", "deepseek", "llama", "qwen", "mistral", "colbert", "rlhf", "je pa"},
        "cv": {"computer vision", "point cloud", "lidar", "object detection", "image segmentation", "mask2former", "multi-view geometry"},
        "mlops": {"mlops", "kubernetes", "docker", "mlflow", "kubeflow", "kafka", "airflow", "fastapi", "tensorrt", "onnx", "kserve"},
        "research": {"research", "bayesian", "uncertainty quantification", "geometric deep learning", "physics-informed", "physical ai", "world model", "robotics"},
        "cloud": {"aws", "gcp", "vertex ai", "sagemaker", "prometheus", "grafana"},
    }

    def _run(self, jobs_json: str) -> List[Dict[str, Any]]:
        try:
            jobs = json.loads(jobs_json) if isinstance(jobs_json, str) else jobs_json
        except json.JSONDecodeError:
            return [{"error": "Invalid JSON input"}]

        all_skills = set()
        for group in self.PROFILE_SKILLS.values():
            all_skills.update(group)

        scored = []
        for job in jobs:
            title = job.get("title", "").lower()
            summary = job.get("summary", "").lower() or job.get("comment_text", "").lower()
            full_text = f"{title} {summary}"

            score = 0
            matched_skills = []

            for group_name, skills in self.PROFILE_SKILLS.items():
                for skill in skills:
                    if skill.lower() in full_text:
                        score += 2
                        matched_skills.append(skill)

            # Bonus for leadership roles
            if any(w in title for w in ["lead", "senior", "principal", "head", "staff"]):
                score += 5
                matched_skills.append("senior/lead role")

            # Bonus for remote
            if job.get("remote"):
                score += 3
                matched_skills.append("remote")

            # Bonus for research
            if "research" in full_text:
                score += 4
                matched_skills.append("research role")

            if score > 0:
                job["match_score"] = score
                job["matched_skills"] = matched_skills
                scored.append(job)

        # Sort by score descending
        scored.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return scored[:50]
