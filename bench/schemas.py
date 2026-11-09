from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Verdict(str, Enum):
    compliant = "compliant"
    partial = "partial"
    non_compliant = "non_compliant"
    insufficient_evidence = "insufficient_evidence"


class CriterionAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    criterion: str
    met: Literal["yes", "no", "unclear"]
    note: str


class Quote(BaseModel):
    model_config = ConfigDict(extra="forbid")
    file: str
    text: str


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Verdict
    justification: str
    criteria_assessment: list[CriterionAssessment]
    quotes: list[Quote]
    recommendation: str
    confidence: float = Field(ge=0.0, le=1.0)


OUTPUT_JSON_SCHEMA = EvaluationResponse.model_json_schema()

