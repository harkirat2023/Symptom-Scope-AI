from pydantic import BaseModel, Field


class SymptomResult(BaseModel):
    id: str = Field(description="Internal symptom identifier (snake_case)")
    name: str = Field(description="Display name for the symptom")
    category: str = Field(description="Body system category")
    relevance_score: float | None = Field(None, ge=0, le=1)


class SymptomSearchResponse(BaseModel):
    results: list[SymptomResult]
    total: int
    categories: list[str]
