from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


class ErrorModel(BaseModel):
    detail: Union[str, List[Dict[str, Any]]]


class ChoiceQuestion(BaseModel):
    type: Literal["choice"]
    prompt: str
    options: Dict[str, str]

    @model_validator(mode="after")
    def validate_question(self):
        if not self.prompt.strip():
            raise ValueError("prompt must not be empty")
        if len(self.options) < 2 or len(self.options) > 255:
            raise ValueError("options must be between 2 and 255")
        return self


class ScoreQuestion(BaseModel):
    type: Literal["score"]
    prompt: str
    min: int
    max: int
    labels: Optional[List[int]] = None

    @model_validator(mode="after")
    def validate_question(self):
        if not self.prompt.strip():
            raise ValueError("prompt must not be empty")
        if self.min >= self.max:
            raise ValueError("min must be less than max")
        if self.labels is not None:
            for value in self.labels:
                if value < self.min or value > self.max:
                    raise ValueError("labels must be within min/max")
        return self


class NoulQuestion(BaseModel):
    type: Literal["noul"]
    prompt: str

    @model_validator(mode="after")
    def validate_question(self):
        if not self.prompt.strip():
            raise ValueError("prompt must not be empty")
        return self


Question = Union[ChoiceQuestion, ScoreQuestion, NoulQuestion]


class DecisionRequest(BaseModel):
    state: str = Field(..., min_length=1)
    questions: Dict[str, Question]


class ChoiceAnswer(BaseModel):
    type: Literal["choice"]
    value: str
    probabilities: Dict[str, float]
    confidence: float


class ScoreAnswer(BaseModel):
    type: Literal["score"]
    value: int
    probabilities: Dict[str, float]
    confidence: float


class NoulAnswer(BaseModel):
    type: Literal["noul"]
    value: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)


class DecisionResponse(BaseModel):
    results: Dict[str, Union[ChoiceAnswer, ScoreAnswer, NoulAnswer]]


class CalibrationExample(BaseModel):
    state: str
    question: Question
    label: Union[str, int, float]


class CalibrationRequest(BaseModel):
    question_type: Literal["choice", "score", "noul"]
    examples: List[CalibrationExample] = Field(min_length=50)
