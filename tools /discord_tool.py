"""
Discord Notification Tool — Sends alerts to a Discord channel via webhook.
Also scrapes public Discord server info where possible.
"""
import json
import time
from typing import List, Dict, Any

import requests
from crewai.tools import BaseTool
from config import DISCORD_WEBHOOK_URL


class DiscordNotifyTool(BaseTool):
    """Send structured research findings to Discord webhook."""
    name: str = "discord_notify"
    description: str = (
        "Sends a summary message to Discord with research findings, "
        "paper alerts, or job vacancy notifications. "
        "Input: JSON string with 'title', 'content', and optional 'color' fields."
    )

    def _run(self, message_data: str) -> Dict[str, str]:
        if not DISCORD_WEBHOOK_URL:
            return {"status": "error", "message": "Discord webhook not configured. Set DISCORD_WEBHOOK_URL in .env"}

        try:
            data = json.loads(message_data) if isinstance(message_data, str) else message_data
        except json.JSONDecodeError:
            data = {"title": "Research Alert", "content": message_data}

        color = data.get("color", 5814783)  # Default: blue
        fields = data.get("fields", [])

        # Discord embeds limit: 25 fields, 1024 chars per field value
        embed = {
            "title": data.get("title", "AI Research Alert")[:256],
            "description": data.get("content", "")[:2048],
            "color": color,
            "fields": [
                {"name": f["name"][:256], "value": f["value"][:1024], "inline": f.get("inline", False)}
                for f in fields[:25]
            ],
            "footer": {"text": "Mohsen Research Agent | Powered by CrewAI"},
            "timestamp": data.get("timestamp", ""),
        }

        try:
            resp = requests.post(
                DISCORD_WEBHOOK_URL,
                json={"embeds": [embed]},
                timeout=10,
            )
            if resp.status_code in (200, 204):
                return {"status": "sent", "message": "Notification sent to Discord"}
            else:
                return {"status": "error", "message": f"Discord returned {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"status": "error", "message": f"Discord send failed: {str(e)}"}


class DiscordWebhookPaperAlertTool(BaseTool):
    """Format and send paper alerts to Discord."""
    name: str = "discord_paper_alert"
    description: str = (
        "Formats a list of papers into Discord embeds and sends them. "
        "Input: JSON array of papers with 'title', 'authors', 'url', 'source' fields."
    )

    def _run(self, papers_json: str) -> Dict[str, Any]:
        if not DISCORD_WEBHOOK_URL:
            return {"status": "error", "message": "Discord webhook not configured"}

        try:
            papers = json.loads(papers_json) if isinstance(papers_json, str) else papers_json
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON"}

        sent = 0
        for paper in papers[:10]:  # Max 10 embeds per message
            authors = paper.get("authors", [])
            author_str = ", ".join(authors[:3]) + ("..." if len(authors) > 3 else "") if isinstance(authors, list) else str(authors)

            embed = {
                "title": paper.get("title", "Untitled")[:256],
                "url": paper.get("url", paper.get("pdf_url", "")),
                "description": paper.get("abstract", "")[:300],
                "color": 3447003,  # Blue for papers
                "fields": [
                    {"name": "Source", "value": paper.get("source", ""), "inline": True},
                    {"name": "Authors", "value": author_str[:1024], "inline": True},
                    {"name": "Published", "value": paper.get("published", paper.get("year", "N/A")), "inline": True},
                ],
                "footer": {"text": "Mohsen Research Agent"},
            }

            try:
                requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
                sent += 1
                time.sleep(0.5)
            except Exception:
                pass

        return {"status": f"sent {sent} paper alerts", "total": len(papers)}
