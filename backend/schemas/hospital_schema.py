
from pydantic import BaseModel


class HospitalResponse(BaseModel):
    id: str | None = None
    name: str
    address: str
    location: str = ""
    phone: str = ""
    rating: float = 0.0
    emergency: bool = False
    specialties: list[str] = []
    has_ambulance: bool = False
    has_emergency_room: bool = False
    latitude: float = 0.0
    longitude: float = 0.0
    image_url: str = ""
    distance_km: float | None = None


class HospitalSearchResponse(BaseModel):
    hospitals: list[HospitalResponse]
    total: int
    locations: list[str] = []
