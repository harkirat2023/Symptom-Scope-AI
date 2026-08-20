
from pydantic import BaseModel


class DoctorResponse(BaseModel):
    id: str | None = None
    name: str
    specialty: str
    location: str
    rating: float = 0.0
    experience_years: int = 0
    hospital: str = ""
    phone: str = ""
    available: bool = True
    consultation_fee: float = 0.0
    image_url: str = ""
    bio: str = ""
    availability: list[str] = []


class DoctorSearchResponse(BaseModel):
    doctors: list[DoctorResponse]
    total: int
    specialties: list[str] = []
    locations: list[str] = []
