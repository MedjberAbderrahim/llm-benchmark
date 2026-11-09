from __future__ import annotations

from pathlib import Path

import pytest

from bench.data_generation import build_dataset
from bench.runner import _check_quotes
from bench.schemas import EvaluationResponse
from bench.scoring import build_metrics


def test_evaluation_schema_accepts_valid_response_and_rejects_unknown_status() -> None:
    valid = {
        "status": "partial", "justification": "One criterion is unmet.",
        "criteria_assessment": [{"criterion": "minimum length", "met": "no", "note": "Observed 8."}],
        "quotes": [{"file": "policy.md", "text": "At least eight characters."}],
        "recommendation": "Raise the enforced minimum.", "confidence": 0.7,
    }
    parsed = EvaluationResponse.model_validate(valid)
    assert parsed.status.value == "partial"
    with pytest.raises(Exception):
        EvaluationResponse.model_validate({**valid, "status": "probably fine"})


def test_quote_check_normalizes_whitespace_case_and_typographic_quotes() -> None:
    output = EvaluationResponse.model_validate({
        "status": "compliant", "justification": "Policy found.", "criteria_assessment": [],
        "quotes": [{"file": "policy.md", "text": "THE  team’s  policy\nrequires review."}],
        "recommendation": "", "confidence": 0.8,
    })
    checked, valid = _check_quotes(output, {"policy.md": "The team's policy requires\nreview."})
    assert valid == 1
    assert checked[0]["valid"] is True


def test_scoring_counts_false_reassurance_and_validity() -> None:
    records = [
        {"expected_status": "non_compliant", "status": "compliant", "matches_expected": False,
         "initial_schema_valid": True, "final_schema_valid": True, "retry_count": 0,
         "quote_validity": {"valid": 1, "total": 1}, "tags": ["injection"], "language": "en",
         "wall_clock_total_seconds": 2.0, "confidence": 0.9},
        {"expected_status": "compliant", "status": "compliant", "matches_expected": True,
         "initial_schema_valid": False, "final_schema_valid": True, "retry_count": 1,
         "quote_validity": {"valid": 0, "total": 1}, "tags": [], "language": "fr",
         "wall_clock_total_seconds": 4.0, "confidence": 0.7},
    ]
    metrics = build_metrics(records, 6.0, {}, {}, "hash", "eval_v1")
    assert metrics["dangerous_false_reassurance_count"] == 1
    assert metrics["repair_retry_count"] == 1
    assert metrics["initial_valid_json_rate"] == 0.5
    assert metrics["final_valid_json_rate"] == 1.0
    assert metrics["quote_validity_rate"] == 0.5


def test_data_generation_is_valid_and_has_stratified_test_split(tmp_path: Path) -> None:
    count = build_dataset(tmp_path)
    assert count == 30
    import yaml
    labels = yaml.safe_load((tmp_path / "data" / "labels.yaml").read_text(encoding="utf-8"))
    test_rows = [row for row in labels if row["split"] == "test"]
    assert len(test_rows) == 10
    assert {row["expected_status"] for row in test_rows} == {
        "compliant", "partial", "non_compliant", "insufficient_evidence"
    }
    assert sum(row["expected_status"] == "insufficient_evidence" for row in labels) >= 3
