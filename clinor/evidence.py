"""Metadata-first evidence discovery. This DOES NOT validate clinical recommendations."""
from __future__ import annotations

import re
from html import unescape

import httpx

from .schemas import Evidence

EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def normalize_abstract(raw: str | None) -> str | None:
    if not raw:
        return None
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]*>", " ", raw))).strip()[:350]


def classify_publication(title: str, kinds: list[str]) -> str:
    text = " ".join([title, *kinds]).lower()
    if any(t in text for t in ("practice guideline", "clinical practice guideline", "guideline")):
        return "guideline_candidate"
    if "systematic review" in text or "meta-analysis" in text:
        return "systematic_review_candidate"
    if any(t in text for t in ("randomized", "randomised", "clinical trial")):
        return "trial_candidate"
    return "other_literature"


def article_to_evidence(article: dict) -> Evidence | None:
    pmid = article.get("pmid")
    doi = article.get("doi")
    pub_id = pmid or article.get("id")
    if not pub_id or not article.get("title"):
        return None
    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else (
        f"https://doi.org/{doi}" if doi else f"https://europepmc.org/article/{article.get('source', 'MED')}/{pub_id}"
    )
    kinds = article.get("pubTypeList", {}).get("pubType", []) or []
    if isinstance(kinds, str):
        kinds = [kinds]
    year = article.get("pubYear")
    return Evidence(
        evidence_id=f"pmid:{pmid}" if pmid else f"epmc:{pub_id}",
        title=unescape(article["title"]),
        url=url, doi=doi, pmid=pmid, publication_date=article.get("firstPublicationDate"),
        source="Europe PMC / PubMed metadata",
        year=int(year) if str(year).isdigit() else None,
        journal=article.get("journalTitle"),
        abstract=normalize_abstract(article.get("abstractText")),
        publication_types=kinds,
        evidence_category=classify_publication(article["title"], kinds),
    )


class EuropePMC:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self.client = client

    async def search(self, query: str, limit: int = 10) -> list[Evidence]:
        params = {"query": query, "format": "json", "resultType": "core", "pageSize": min(limit, 30)}
        if self.client is not None:
            response = await self.client.get(EUROPE_PMC, params=params)
            response.raise_for_status()
            data = response.json()
        else:
            async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
                response = await client.get(EUROPE_PMC, params=params)
                response.raise_for_status()
                data = response.json()
        articles = data.get("resultList", {}).get("result", [])
        return [item for a in articles if (item := article_to_evidence(a)) is not None]


def rank_evidence(records: list[Evidence], limit: int) -> list[Evidence]:
    rank = {"guideline_candidate": 0, "guideline_web_candidate": 1,
            "systematic_review_candidate": 2, "trial_candidate": 3,
            "web_page_candidate": 4, "other_literature": 5}
    unique: dict[str, Evidence] = {}
    for item in records:
        unique[item.evidence_id] = item
    return sorted(unique.values(), key=lambda e: (rank.get(e.evidence_category, 4), -(e.year or 0)))[:limit]
