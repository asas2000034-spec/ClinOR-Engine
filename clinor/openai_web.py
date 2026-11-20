"""Optional model-operated web discovery, preserving official source citation links.

Web-search citations are **discovery candidates** and must be checked manually;
no scraped page text is promoted to a computable medical rule.
"""
from __future__ import annotations

import hashlib
from urllib.parse import urlparse

from .ai import _client
from .schemas import Evidence


def citations_to_evidence(response) -> list[Evidence]:
    records = []
    seen = set()
    for output in getattr(response, "output", []):
        if getattr(output, "type", None) != "message":
            continue
        for part in getattr(output, "content", []):
            for annotation in getattr(part, "annotations", []) or []:
                if getattr(annotation, "type", None) != "url_citation":
                    continue
                url = getattr(annotation, "url", "")
                title = getattr(annotation, "title", "") or "Cited search result"
                parsed = urlparse(url)
                if parsed.scheme != "https" or not parsed.netloc or url in seen:
                    continue
                seen.add(url)
                key = hashlib.sha256(url.encode()).hexdigest()[:16]
                records.append(Evidence(
                    evidence_id=f"aiweb:{key}", title=title[:400], url=url,
                    source=f"OpenAI web-search citation / {parsed.netloc} (unverified)",
                    evidence_category="guideline_web_candidate" if "guideline" in title.lower()
                    else "web_page_candidate",
                    publication_types=["ai_web_search_citation"],
                ))
    return records


class OpenAIWebGuidelineSearch:
    def search(self, condition: str, jurisdiction: str = "international") -> list[Evidence]:
        topic = " ".join("".join(ch if ch.isalnum() or ch.isspace() else " " for ch in condition).split())
        request = (
            f"Find current official clinical practice guideline publisher pages relevant to: {topic}. "
            f"Country preference: {jurisdiction}. Prefer national and specialty guideline publishers, "
            "not general discussion forums. Cite source URLs. Do not offer treatment advice or patient-specific prescriptions. "
            "If uncertain about currency or version, say it is unverified."
        )
        response = _client().responses.create(
            model=__import__("os").environ.get("OPENAI_WEB_MODEL", "gpt-4.1-mini"),
            tools=[{"type": "web_search"}],
            input=request,
            include=["web_search_call.action.sources"],
        )
        return citations_to_evidence(response)
