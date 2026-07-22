from pydantic import BaseModel
from typing import Optional


class DoctorResponse(BaseModel):
    id: Optional[str] = None
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
