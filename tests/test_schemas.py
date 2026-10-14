import pytest
from pydantic import ValidationError

from schemas.step0_refinement import RefinementOutput
from schemas.step1_dod import DoDOutput


def test_refinement_valid():
    out = RefinementOutput(refined_ticket="do X", gaps=[], questions=[], assumptions=["a"])
    assert out.refined_ticket == "do X"


def test_refinement_rejects_bad_severity():
    with pytest.raises(ValidationError):
        RefinementOutput(
            refined_ticket="do X",
            gaps=[{"area": "s", "description": "d", "severity": "critical"}],
            questions=[],
            assumptions=[],
        )


def test_dod_requires_contracts():
    with pytest.raises(ValidationError):
        DoDOutput(contracts=[], dod=[], milestones=[])


def test_dod_valid():
    out = DoDOutput(
        contracts=[{"kind": "json", "name": "r", "schema_ref": "S", "status_codes": [200]}],
        dod=[{"criterion": "works", "verifiable": True}],
        milestones=[{"order": 1, "title": "m1", "acceptance": "done"}],
    )
    assert len(out.contracts) == 1
