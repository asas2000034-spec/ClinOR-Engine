from clinor.optimizer import optimize
from clinor.schemas import OptimizeRequest, TreatmentOption


def test_synthetic_optimum():
    request = OptimizeRequest(
        options=[TreatmentOption(option_id="A", label="A", benefit=10, burden=1, cost=2),
                 TreatmentOption(option_id="B", label="B", benefit=8, burden=1, cost=3)],
        max_selections=1,
    )
    output = optimize(request)
    assert output.status == "optimal"
    assert output.selected == ["A"]
    assert output.clinical_authorization == "not_authorized"


def test_hard_exclusions_are_enforced():
    request = OptimizeRequest(
        options=[TreatmentOption(option_id="A", label="A", benefit=100, burden=0, cost=1, forbidden=True),
                 TreatmentOption(option_id="B", label="B", benefit=10, burden=0, cost=1)],
    )
    assert optimize(request).selected == ["B"]


def test_unfeasible_is_not_softened():
    request = OptimizeRequest(
        options=[TreatmentOption(option_id="A", label="A", benefit=100, burden=0, cost=1, forbidden=True)],
        min_selections=1,
    )
    assert optimize(request).status == "infeasible"


def test_clinical_requires_reviewed_pack():
    request = OptimizeRequest(mode="clinical", options=[
        TreatmentOption(option_id="A", label="A", benefit=10, burden=1, cost=1)])
    assert optimize(request).status == "review_required"


def test_incompatible_pair_not_selected():
    request = OptimizeRequest(
        options=[TreatmentOption(option_id="A", label="A", benefit=90, burden=1, cost=1, incompatible_with=["B"]),
                 TreatmentOption(option_id="B", label="B", benefit=80, burden=1, cost=1)],
        max_selections=2)
    assert len(optimize(request).selected) == 1


def test_prerequisite_is_enforced():
    req = OptimizeRequest(options=[
        TreatmentOption(option_id="A", label="A", benefit=100, burden=0, cost=1, requires=["B"]),
        TreatmentOption(option_id="B", label="B", benefit=1, burden=0, cost=1)],
        max_selections=1)
    result = optimize(req)
    assert result.selected == ["B"]


def test_budget_constraint():
    req = OptimizeRequest(options=[
        TreatmentOption(option_id="A", label="A", benefit=100, burden=0, cost=200),
        TreatmentOption(option_id="B", label="B", benefit=20, burden=0, cost=10)],
        budget=25)
    assert optimize(req).selected == ["B"]
