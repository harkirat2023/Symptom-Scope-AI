from pydantic import BaseModel, Field


class DoctorResponse(BaseModel):
    name: str
    specialty: str
    location: str
    rating: float = Field(ge=0, le=5)
    distance_km: float = Field(ge=0)
    availability: str
    photo_url: str | None = None


class DoctorSearchResponse(BaseModel):
    results: list[DoctorResponse]
    total: int
    specialties: list[str]
    locations: list[str]
