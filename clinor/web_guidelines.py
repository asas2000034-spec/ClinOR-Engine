"""Optional web index for locating guideline publisher pages (metadata only)."""
from __future__ import annotations

import hashlib
import os
from html import unescape
from urllib.parse import urlparse

import httpx

from .schemas import Evidence

BRAVE_API = "https://api.search.brave.com/res/v1/web/search"


def web_hit_to_evidence(hit: dict) -> Evidence | None:
    url = hit.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc or not hit.get("title"):
        return None
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    title = unescape(hit["title"])
    summary = unescape(hit.get("description", ""))
    return Evidence(
        evidence_id=f"web:{key}", title=title[:400], url=url,
        source=f"Brave web index / {parsed.netloc} (publisher not verified)",
        abstract=summary[:1100] or None,
        evidence_category="guideline_web_candidate" if "guideline" in title.lower() else "web_page_candidate",
        publication_types=["web_search_result"],
    )


class BraveGuidelineSearch:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self.client = client

    async def search(self, condition: str, jurisdiction: str = "international",
                     limit: int = 8) -> list[Evidence]:
        api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not api_key:
            return []
        # Topic only: do not send a patient profile, named person or complete chart.
        topic = " ".join("".join(ch if ch.isalnum() or ch.isspace() else " " for ch in condition).split())
        region = jurisdiction if jurisdiction != "international" else ""
        query = f"{topic} clinical practice guideline treatment recommendations {region}"[:250]
        params = {"q": query, "count": min(limit, 20)}
        headers = {"X-Subscription-Token": api_key, "Accept": "application/json"}
        if self.client is not None:
            response = await self.client.get(BRAVE_API, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        else:
            async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
                response = await client.get(BRAVE_API, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
        hits = data.get("web", {}).get("results", [])
        return [item for h in hits if (item := web_hit_to_evidence(h)) is not None]
