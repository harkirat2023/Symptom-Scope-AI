from pydantic import BaseModel, Field


class HospitalResponse(BaseModel):
    name: str
    location: str
    specialties: list[str]
    rating: float = Field(ge=0, le=5)
    distance_km: float = Field(ge=0)
    phone: str
    has_emergency: bool
    bed_count: int = Field(ge=0)


class HospitalSearchResponse(BaseModel):
    results: list[HospitalResponse]
    total: int
    locations: list[str]
    specialties: list[str]
