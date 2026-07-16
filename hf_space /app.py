"""
Mohsen's AI Research & Vacancy Intelligence Agent — Hugging Face Spaces
Gradio Web Interface with 6 tabs.

Deploy: Push this folder to HF Spaces (free CPU tier works!)
"""

import gradio as gr
import json
from datetime import datetime

from hf_tools import (
    search_arxiv, arxiv_category_feed,
    search_semantic_scholar, track_author_papers,
    github_trending, github_releases,
    search_hackernews, hn_who_is_hiring,
    search_openalex, openalex_institution_papers,
    search_crossref, score_vacancy,
)

# ─── Helpers ──────────────────────────────────────────────────────

def _fmt_paper(p):
    """Format a paper dict into a readable markdown string."""
    if p.get("error"):
        return f"⚠️ {p.get('title', 'Unknown error')}"
    authors = p.get("authors", "N/A")
    date = p.get("published", p.get("date", p.get("year", "")))
    url = p.get("url", p.get("pdf_url", ""))
    link = f" [🔗]({url})" if url else ""
    citations = p.get("citations", p.get("citation_count", ""))
    cit_str = f" | 📊 Citations: **{citations}**" if citations else ""
    venue = p.get("venue", "")
    ven_str = f" | 📰 {venue}" if venue else ""
    abstract = p.get("abstract", "")
    abs_str = f"\n> {abstract}" if abstract else ""
    return f"### {p.get('title', 'Untitled')}{link}\n**{authors}** | 📅 {date}{cit_str}{ven_str}{abs_str}"


def _fmt_repo(r):
    """Format a GitHub repo dict."""
    if r.get("error"):
        return f"⚠️ {r.get('title', 'Unknown error')}"
    link = f" [🔗]({r['url']})" if r.get("url") else ""
    topics = f"\n🏷️ {r['topics']}" if r.get("topics") else ""
    return f"### ⭐ {r.get('name', '')} — {r.get('stars', 0)}⭐{link}\n{r.get('description', '')}{topics}\n👨‍💻 {r.get('language', '')} | 📜 {r.get('license', '')}"


def _fmt_hn(h):
    """Format a HN story dict."""
    if h.get("error"):
        return f"⚠️ {h.get('title', 'Unknown error')}"
    link = f" [🔗]({h['url']})" if h.get("url") else ""
    return f"**{h.get('title', '')}**{link}\n⬆️ {h.get('points', 0)} pts | 💬 {h.get('comments', 0)} comments | 👤 {h.get('author', '')} | 📅 {h.get('date', '')}"


def _fmt_vacancy(v):
    """Format a vacancy dict."""
    if v.get("error"):
        return f"⚠️ {v.get('title', 'Unknown error')}"
    score = v.get("match_score", 0)
    skills = v.get("matched_skills", [])
    skills_str = ", ".join(skills[:8]) if skills else ""
    link = f" [🔗]({v['url']})" if v.get("url") else ""
    emoji = "🟢" if score >= 15 else "🟡" if score >= 8 else "🔴"
    return f"{emoji} **Score: {score}** | {v.get('title', '')}{link}\nMatched: {skills_str}"


def _fmt_release(r):
    """Format a GitHub release."""
    if r.get("error"):
        return f"⚠️ {r.get('title', 'Unknown error')}"
    link = f" [🔗]({r['url']})" if r.get("url") else ""
    body = r.get("body", "")
    body_str = f"\n> {(body[:300] + '...') if body else 'No details'}"
    return f"### {r.get('title', r.get('tag', ''))}{link}\n📅 {r.get('published', '')}{body_str}"


# ═══════════════════════════════════════════════════════════════════
# TAB 1: FULL INTELLIGENCE REPORT
# ═══════════════════════════════════════════════════════════════════

def run_full_report(progress=gr.Progress()):
    """Run all sources and produce a comprehensive report."""
    sections = []
    total_steps = 9
    step = 0

    def _update(label):
        nonlocal step
        step += 1
        progress(step / total_steps, desc=label)

    # 1. arXiv — Physical AI & World Models
    _update("Searching arXiv: Physical AI & World Models...")
    arxiv_papers = search_arxiv("physical AI world model JEPA embodied", max_results=5)
    sections.append("## 📚 arXiv: Physical AI & World Models\n" +
                    "\n---\n".join(_fmt_paper(p) for p in arxiv_papers if not p.get("error")))

    # 2. arXiv — Robotics & CV
    _update("Searching arXiv: Robotics & Computer Vision...")
    arxiv_cv = search_arxiv("robotics foundation model 3D point cloud", max_results=5)
    sections.append("## 🤖 arXiv: Robotics & Computer Vision\n" +
                    "\n---\n".join(_fmt_paper(p) for p in arxiv_cv if not p.get("error")))

    # 3. Semantic Scholar — Yann LeCun
    _update("Tracking Yann LeCun papers via Semantic Scholar...")
    lecitin = track_author_papers("Yann LeCun", max_results=5)
    sections.append("## 🧑‍🔬 Yann LeCun — Recent Papers\n" +
                    "\n---\n".join(_fmt_paper(p) for p in lecitin if not p.get("error")))

    # 4. OpenAlex — NYU
    _update("Fetching NYU papers via OpenAlex...")
    nyu = openalex_institution_papers("New York University", max_results=5)
    sections.append("## 🏛️ NYU — Recent AI Papers\n" +
                    "\n---\n".join(_fmt_paper(p) for p in nyu if not p.get("error")))

    # 5. OpenAlex — Meta FAIR
    _update("Fetching Meta FAIR papers via OpenAlex...")
    fair = openalex_institution_papers("Meta AI", max_results=5)
    sections.append("## 🔬 Meta FAIR — Recent Papers\n" +
                    "\n---\n".join(_fmt_paper(p) for p in fair if not p.get("error")))

    # 6. GitHub Trending
    _update("Checking GitHub trending AI repos...")
    repos = github_trending("agentic-ai", max_results=5)
    sections.append("## ⭐ GitHub Trending: Agentic AI\n" +
                    "\n---\n".join(_fmt_repo(r) for r in repos if not r.get("error")))

    # 7. Hacker News
    _update("Searching Hacker News...")
    hn = search_hackernews("agentic AI framework LLM", max_results=5)
    sections.append("## 🔥 Hacker News: Trending AI\n" +
                    "\n---\n".join(_fmt_hn(h) for h in hn if not h.get("error")))

    # 8. GitHub Releases
    _update("Fetching latest AI framework releases...")
    releases = github_releases("huggingface/transformers,pytorch/pytorch,vllm-project/vllm", max_per_repo=1)
    sections.append("## 🚀 Latest AI Framework Releases\n" +
                    "\n---\n".join(_fmt_release(r) for r in releases if not r.get("error")))

    # 9. HN Who is Hiring
    _update("Scanning HN Who is Hiring for AI jobs...")
    hiring = hn_who_is_hiring(max_results=10)

    # Score vacancies
    scored = []
    for h in hiring:
        text = f"{h.get('title', '')} {h.get('source', '')}"
        score, skills = score_vacancy(text)
        h["match_score"] = score
        h["matched_skills"] = skills
        scored.append(h)
    scored.sort(key=lambda x: x.get("match_score", 0), reverse=True)

    sections.append("## 💼 HN Who is Hiring — AI Jobs (Profile-Matched)\n" +
                    "\n---\n".join(_fmt_vacancy(v) for v in scored[:10] if not v.get("error")))

    header = f"""# 🔬 AI Research Intelligence Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}  
**Profile:** Mohsen Mostafa — Physical & Geometric AI | AI Team Lead  
**Sources:** arXiv, Semantic Scholar, OpenAlex, GitHub, Hacker News (all free APIs)

---

"""
    return header + "\n\n---\n\n".join(sections)


# ═══════════════════════════════════════════════════════════════════
# TAB 2: ACADEMIC PAPERS
# ═══════════════════════════════════════════════════════════════════

def run_academic_search(query, source, author_name, institution, progress=gr.Progress()):
    results = []
    if query:
        progress(0.2, desc="Searching papers...")
        if source == "arXiv":
            results = search_arxiv(query, 10)
        elif source == "Semantic Scholar":
            results = search_semantic_scholar(query, 10)
        elif source == "OpenAlex":
            results = search_openalex(query, 10)
        elif source == "CrossRef":
            results = search_crossref(query, 10)
        elif source == "All Sources":
            progress(0.1, desc="arXiv...")
            results = search_arxiv(query, 5)
            progress(0.4, desc="Semantic Scholar...")
            results += search_semantic_scholar(query, 5)
            progress(0.7, desc="OpenAlex...")
            results += search_openalex(query, 5)

    if author_name:
        progress(0.8, desc=f"Tracking {author_name}...")
        results += track_author_papers(author_name, 5)

    if institution:
        progress(0.9, desc=f"Fetching {institution} papers...")
        results += openalex_institution_papers(institution, 5)

    if not results:
        return "No results. Enter a query, author, or institution."

    output = f"# 📚 Academic Paper Search Results\n\n"
    output += f"**Query:** {query} | **Source:** {source} | **Author:** {author_name} | **Institution:** {institution}\n\n"
    output += "---\n\n".join(_fmt_paper(p) for p in results if not p.get("error"))
    errors = [p.get("title", "") for p in results if p.get("error")]
    if errors:
        output += f"\n\n⚠️ Errors: {'; '.join(errors)}"
    return output


# ═══════════════════════════════════════════════════════════════════
# TAB 3: INDUSTRIAL / FRAMEWORKS
# ═══════════════════════════════════════════════════════════════════

def run_industrial_search(topic, search_type, progress=gr.Progress()):
    results = []

    if search_type == "Trending Repos":
        progress(0.3, desc=f"GitHub trending: {topic}...")
        results = github_trending(topic, 10)
        output = f"# ⭐ GitHub Trending: {topic}\n\n"
        output += "\n---\n\n".join(_fmt_repo(r) for r in results if not r.get("error"))

    elif search_type == "Framework Releases":
        progress(0.3, desc=f"Fetching releases for {topic}...")
        results = github_releases(topic, 2)
        output = f"# 🚀 Latest Releases\n\n"
        output += "\n---\n\n".join(_fmt_release(r) for r in results if not r.get("error"))

    elif search_type == "HN Discussions":
        progress(0.3, desc=f"HN search: {topic}...")
        results = search_hackernews(topic, 10)
        output = f"# 🔥 Hacker News: {topic}\n\n"
        output += "\n---\n\n".join(_fmt_hn(h) for h in results if not h.get("error"))

    elif search_type == "All Industrial":
        progress(0.1, desc="GitHub trending...")
        repos = github_trending(topic, 5)
        progress(0.4, desc="HN discussions...")
        hn = search_hackernews(topic, 5)
        results = repos + hn
        output = f"# 🏭 Industrial Intelligence: {topic}\n\n"
        output += "## ⭐ Trending Repos\n\n"
        output += "\n---\n\n".join(_fmt_repo(r) for r in repos if not r.get("error"))
        output += "\n\n## 🔥 Hacker News\n\n"
        output += "\n---\n\n".join(_fmt_hn(h) for h in hn if not h.get("error"))

    if not output.strip().split("\n")[-1]:
        output += "No results found."
    return output


# ═══════════════════════════════════════════════════════════════════
# TAB 4: VACANCY SCOUT
# ═══════════════════════════════════════════════════════════════════

def run_vacancy_search(role_keywords, progress=gr.Progress()):
    progress(0.1, desc="Searching HN Who is Hiring...")
    hiring = hn_who_is_hiring(max_results=20)

    progress(0.5, desc="Searching HN for specific roles...")
    for kw in [k.strip() for k in role_keywords.split(",")[:4]]:
        stories = search_hackernews(f"{kw} hiring OR jobs OR vacancy", 5)
        for s in stories:
            s["source"] = f"HN [{kw}]"
            hiring.append(s)

    progress(0.8, desc="Scoring against profile...")
    scored = []
    for h in hiring:
        text = f"{h.get('title', '')} {h.get('source', '')}"
        score, skills = score_vacancy(text)
        h["match_score"] = score
        h["matched_skills"] = skills
        scored.append(h)
    scored.sort(key=lambda x: x.get("match_score", 0), reverse=True)

    progress(1.0, desc="Done!")
    output = f"# 💼 AI Job Vacancies — Profile Matched\n"
    output += f"**Roles searched:** {role_keywords}\n"
    output += f"**Total found:** {len(scored)} | **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
    output += "---\n\n".join(_fmt_vacancy(v) for v in scored[:25] if not v.get("error"))

    if not output.strip().split("\n")[-1]:
        output += "\n\nNo matching vacancies found. Try broader keywords."
    return output


# ═══════════════════════════════════════════════════════════════════
# TAB 5: CUSTOM SEARCH (any query across all sources)
# ═══════════════════════════════════════════════════════════════════

def run_custom_search(query, include_arxiv, include_ss, include_oa, include_hn, include_gh, progress=gr.Progress()):
    results = []
    step = 0
    total = sum([include_arxiv, include_ss, include_oa, include_hn, include_gh])
    if total == 0:
        return "Select at least one source!"

    if include_arxiv:
        step += 1
        progress(step / total, desc="arXiv...")
        results += search_arxiv(query, 5)

    if include_ss:
        step += 1
        progress(step / total, desc="Semantic Scholar...")
        results += search_semantic_scholar(query, 5)

    if include_oa:
        step += 1
        progress(step / total, desc="OpenAlex...")
        results += search_openalex(query, 5)

    if include_hn:
        step += 1
        progress(step / total, desc="Hacker News...")
        results += search_hackernews(query, 5)

    if include_gh:
        step += 1
        progress(step / total, desc="GitHub...")
        results += github_trending(query, 5)

    if not results:
        return f"No results for '{query}'."

    # Separate papers from repos from HN stories
    paper_sources = {"arXiv", "Semantic Scholar", "OpenAlex", "CrossRef"}
    papers = [r for r in results if r.get("source", "").split(" [")[0] in paper_sources and not r.get("error")]
    repos = [r for r in results if r.get("source", "") == "GitHub" and not r.get("error")]
    hn = [r for r in results if r.get("source", "") == "Hacker News" and not r.get("error")]

    output = f"# 🔍 Custom Search: \"{query}\"\n"
    output += f"**Found:** {len(papers)} papers, {len(repos)} repos, {len(hn)} HN stories\n\n"

    if papers:
        output += "## 📚 Papers\n\n" + "\n---\n\n".join(_fmt_paper(p) for p in papers)
    if repos:
        output += "\n\n## ⭐ Repositories\n\n" + "\n---\n\n".join(_fmt_repo(r) for r in repos)
    if hn:
        output += "\n\n## 🔥 Hacker News\n\n" + "\n---\n\n".join(_fmt_hn(h) for h in hn)

    errors = [r.get("title", "") for r in results if r.get("error")]
    if errors:
        output += f"\n\n⚠️ Some sources failed: {'; '.join(errors[:3])}"
    return output


# ═══════════════════════════════════════════════════════════════════
# TAB 6: API STATUS
# ═══════════════════════════════════════════════════════════════════

def test_all_apis():
    tests = [
        ("arXiv", lambda: search_arxiv("test", 1)),
        ("Semantic Scholar", lambda: search_semantic_scholar("AI", 1)),
        ("GitHub", lambda: github_trending("AI", 1)),
        ("Hacker News", lambda: search_hackernews("AI", 1)),
        ("OpenAlex", lambda: search_openalex("AI", 1)),
        ("CrossRef", lambda: search_crossref("AI", 1)),
    ]
    output = "# 🧪 API Connectivity Test\n\n"
    output += "| API | Status | Details |\n|-----|--------|--------|\n"
    for name, fn in tests:
        try:
            r = fn()
            ok = len([x for x in r if not x.get("error")]) > 0
            if ok:
                count = len([x for x in r if not x.get("error")])
                output += f"| ✅ {name} | **Working** | {count} result(s) |\n"
            else:
                err = r[0].get("title", "Unknown") if r else "No response"
                output += f"| ❌ {name} | **Failed** | {err[:60]} |\n"
        except Exception as e:
            output += f"| ❌ {name} | **Error** | {str(e)[:60]} |\n"
    output += f"\n**Test completed:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
    return output


# ═══════════════════════════════════════════════════════════════════
# BUILD GRADIO INTERFACE
# ═══════════════════════════════════════════════════════════════════

def create_app():
    with gr.Blocks(
        title="Mohsen's AI Research Agent",
    ) as app:

        gr.Markdown(
            """
            # 🔬 Mohsen's AI Research & Vacancy Intelligence Agent
            **Physical & Geometric AI** | AI Team Lead | 15+ Free APIs | CrewAI + Google ADK

            *Automatically fetches the latest research papers, frameworks, community trends, and job vacancies
            tailored to Mohsen Mostafa's research profile.*
            """
        )

        with gr.Tabs():
            # ─── TAB 1: Full Report ───
            with gr.Tab("📋 Full Report"):
                gr.Markdown("Run all 6 free API sources at once for a comprehensive intelligence report.")
                btn_full = gr.Button("🚀 Generate Full Report", variant="primary", size="lg")
                out_full = gr.Markdown(label="Report")
                btn_full.click(fn=run_full_report, outputs=out_full)

            # ─── TAB 2: Academic Papers ───
            with gr.Tab("📚 Academic Papers"):
                with gr.Row():
                    query = gr.Textbox(label="Search Query", placeholder="e.g. world model JEPA, physical AI robotics",
                                       scale=3)
                    source = gr.Dropdown(
                        choices=["arXiv", "Semantic Scholar", "OpenAlex", "CrossRef", "All Sources"],
                        value="arXiv", label="Source", scale=1)
                with gr.Row():
                    author = gr.Textbox(label="Track Author", placeholder="e.g. Yann LeCun", scale=1)
                    inst = gr.Dropdown(
                        choices=["New York University", "Meta AI", "DeepMind", "MIT CSAIL",
                                 "Stanford University", "ETH Zurich", "CMU"],
                        label="Institution", scale=1, allow_custom_value=True)
                    btn_academic = gr.Button("🔍 Search", variant="primary", scale=1)
                out_academic = gr.Markdown()
                btn_academic.click(fn=run_academic_search,
                                   inputs=[query, source, author, inst],
                                   outputs=out_academic)

            # ─── TAB 3: Industrial / Frameworks ───
            with gr.Tab("🏭 Industrial & Frameworks"):
                with gr.Row():
                    topic = gr.Textbox(label="Topic", placeholder="e.g. agentic-ai, mlops, llm-agent, TensorRT",
                                       value="agentic-ai", scale=3)
                    stype = gr.Dropdown(
                        choices=["Trending Repos", "Framework Releases", "HN Discussions", "All Industrial"],
                        value="Trending Repos", label="Search Type", scale=1)
                btn_industrial = gr.Button("🔍 Search", variant="primary")
                out_industrial = gr.Markdown()
                btn_industrial.click(fn=run_industrial_search, inputs=[topic, stype], outputs=out_industrial)

            # ─── TAB 4: Vacancy Scout ───
            with gr.Tab("💼 Vacancy Scout"):
                gr.Markdown(
                    "Searches HN 'Who is Hiring' and filters for AI/ML/CV/Robotics positions. "
                    "Each vacancy is **scored against Mohsen's profile** (PyTorch, LLMs, CV, MLOps, research, leadership)."
                )
                roles = gr.Textbox(
                    label="Role Keywords (comma-separated)",
                    value="AI Research Engineer, Computer Vision, AI Team Lead, MLOps, LLM Engineer, Robotics AI",
                    lines=2)
                btn_vacancy = gr.Button("💼 Find Vacancies", variant="primary")
                out_vacancy = gr.Markdown()
                btn_vacancy.click(fn=run_vacancy_search, inputs=[roles], outputs=out_vacancy)

            # ─── TAB 5: Custom Search ───
            with gr.Tab("🔍 Custom Search"):
                custom_query = gr.Textbox(label="Search Query", placeholder="Any query across all sources...",
                                          lines=2)
                with gr.Row():
                    chk_arxiv = gr.Checkbox(label="arXiv", value=True)
                    chk_ss = gr.Checkbox(label="Semantic Scholar", value=True)
                    chk_oa = gr.Checkbox(label="OpenAlex", value=True)
                    chk_hn = gr.Checkbox(label="Hacker News", value=True)
                    chk_gh = gr.Checkbox(label="GitHub", value=False)
                btn_custom = gr.Button("🔍 Search All", variant="primary")
                out_custom = gr.Markdown()
                btn_custom.click(fn=run_custom_search,
                                 inputs=[custom_query, chk_arxiv, chk_ss, chk_oa, chk_hn, chk_gh],
                                 outputs=out_custom)

            # ─── TAB 6: API Status ───
            with gr.Tab("🧪 API Status"):
                gr.Markdown("Test connectivity to all 6 free API sources.")
                btn_test = gr.Button("🧪 Run Test", variant="secondary")
                out_test = gr.Markdown()
                btn_test.click(fn=test_all_apis, outputs=out_test)

        gr.Markdown(
            """
            ---
            **Built for:** Mohsen Mostafa — [Research Profile](https://mohsenmostafa1.github.io/Mohsen.github.io/) | ORCID: 0009-0004-4478-0317
            **Stack:** Gradio + CrewAI + Google ADK | **APIs:** arXiv, Semantic Scholar, OpenAlex, CrossRef, GitHub, Hacker News
            """
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="cyan"),
        css="""
            .gradio-container { max-width: 1200px; }
            .tab-title { font-size: 1.1em; font-weight: bold; }
            footer { display: none !important; }
        """
    )
