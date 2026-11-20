from clinor.evidence import article_to_evidence, rank_evidence
from clinor.research import research
from clinor.schemas import ResearchRequest


def test_metadata_and_category():
    record = {"pmid": "12345", "title": "A clinical practice guideline",
              "pubYear": "2026", "pubTypeList": {"pubType": ["Guideline"]},
              "abstractText": "<p>Abstract content.</p>"}
    evidence = article_to_evidence(record)
    assert evidence.evidence_id == "pmid:12345"
    assert evidence.evidence_category == "guideline_candidate"
    assert evidence.abstract == "Abstract content."
    assert rank_evidence([evidence, evidence], 10) == [evidence]


async def test_consent_blocks_external_requests():
    class ExplodingProvider:
        async def search(self, query, limit=5):
            raise AssertionError("No outbound requests without consent")
    resp = await research(ResearchRequest(condition="any condition"), provider=ExplodingProvider())
    assert resp.status == "consent_required"
    assert resp.evidence == []


async def test_discovery_is_condition_agnostic():
    class FakeProvider:
        async def search(self, query, limit=5):
            return [article_to_evidence({"pmid": "99999", "title": "Some published guideline", "pubYear": "2025"})]
    for condition in ["asthma", "rheumatoid arthritis", "heart failure", "migraine"]:
        response = await research(ResearchRequest(condition=condition, consent_external_search=True,
                                                 use_ai=False), provider=FakeProvider())
        assert response.status == "completed"
        assert len(response.evidence) == 1
        assert response.evidence[0].status == "discovered_unverified"


def test_guideline_web_discovery_metadata():
    from clinor.web_guidelines import web_hit_to_evidence
    hit = {"title": "Clinical Practice Guidelines", "url": "https://www.who.int/health-topics/",
           "description": "Guidance page (unverified)"}
    record = web_hit_to_evidence(hit)
    assert record.evidence_id.startswith("web:")
    assert record.status == "discovered_unverified"
    assert record.evidence_category == "guideline_web_candidate"
    assert web_hit_to_evidence({"title":"Bad", "url":"javascript:alert(1)"}) is None


def test_ai_web_citations_require_https_and_real_annotations():
    from types import SimpleNamespace as N

    from clinor.openai_web import citations_to_evidence
    citation = N(type="url_citation", title="Example guideline", url="https://www.who.int/example")
    bad = N(type="url_citation", title="Bad", url="javascript:alert(1)")
    output = N(type="message", content=[N(annotations=[citation, citation, bad])])
    result = citations_to_evidence(N(output=[output]))
    assert len(result) == 1
    assert result[0].evidence_category == "guideline_web_candidate"
    assert result[0].status == "discovered_unverified"
