"""MongoDB repository for hospital data."""

from datetime import datetime, timezone
from typing import Optional
from utils.database import get_database

_COLLECTION = None


def _get_collection():
    global _COLLECTION
    if _COLLECTION is None:
        _COLLECTION = get_database()["hospitals"]
    return _COLLECTION


async def ensure_indexes():
    col = _get_collection()
    await col.create_index("location")
    await col.create_index("specialties")
    await col.create_index("has_emergency")
    await col.create_index([("name", 1)], unique=True)


async def seed_hospitals():
    """Seed the hospitals collection with default data if empty."""
    col = _get_collection()
    existing = await col.count_documents({})
    if existing > 0:
        return

    hospitals = [
        {"name": "Dayanand Medical College & Hospital", "location": "Ludhiana", "specialties": ["Cardiology", "Neurology", "Pulmonology", "General Medicine", "Emergency"], "rating": 4.6, "distance_km": 1.5, "phone": "+91-161-4688888", "has_emergency": True, "has_ambulance": True, "bed_count": 1200, "address": "Civil Lines, Ludhiana"},
        {"name": "Christian Medical College & Hospital", "location": "Ludhiana", "specialties": ["Cardiology", "Neurology", "Gastroenterology", "General Medicine", "Emergency", "Orthopedics"], "rating": 4.8, "distance_km": 3.0, "phone": "+91-161-5032255", "has_emergency": True, "has_ambulance": True, "bed_count": 1800, "address": "Brown Road, Ludhiana"},
        {"name": "Fortis Hospital", "location": "Ludhiana", "specialties": ["Cardiology", "Neurology", "General Medicine", "Emergency"], "rating": 4.5, "distance_km": 4.2, "phone": "+91-161-4610100", "has_emergency": True, "has_ambulance": True, "bed_count": 350, "address": "Vikas Nagar, Ludhiana"},
        {"name": "Apollo Hospitals", "location": "Amritsar", "specialties": ["Cardiology", "Neurology", "Pulmonology", "Gastroenterology", "Emergency"], "rating": 4.7, "distance_km": 2.1, "phone": "+91-183-5088888", "has_emergency": True, "has_ambulance": True, "bed_count": 500, "address": "Queens Road, Amritsar"},
        {"name": "Surya Hospital", "location": "Amritsar", "specialties": ["General Medicine", "Pediatrics", "Orthopedics"], "rating": 4.2, "distance_km": 1.8, "phone": "+91-183-5012345", "has_emergency": True, "has_ambulance": False, "bed_count": 150, "address": "Mall Road, Amritsar"},
        {"name": "Patiala Government Medical College", "location": "Patiala", "specialties": ["General Medicine", "Cardiology", "Neurology", "Pulmonology", "Emergency"], "rating": 4.1, "distance_km": 2.5, "phone": "+91-175-3046000", "has_emergency": True, "has_ambulance": True, "bed_count": 900, "address": "Rajindra Hospital Rd, Patiala"},
        {"name": "Jalandhar Civil Hospital", "location": "Jalandhar", "specialties": ["General Medicine", "Pediatrics", "Emergency"], "rating": 3.8, "distance_km": 1.2, "phone": "+91-181-5012345", "has_emergency": True, "has_ambulance": True, "bed_count": 400, "address": "GT Road, Jalandhar"},
        {"name": "Shiv Hospital & Medical Centre", "location": "Jalandhar", "specialties": ["General Medicine", "Gastroenterology", "Orthopedics"], "rating": 4.0, "distance_km": 3.3, "phone": "+91-181-5078901", "has_emergency": False, "has_ambulance": True, "bed_count": 80, "address": "Model Town, Jalandhar"},
        {"name": "Max Super Speciality Hospital", "location": "Ludhiana", "specialties": ["Cardiology", "Neurology", "Pulmonology", "Gastroenterology", "Emergency", "Orthopedics", "Pediatrics"], "rating": 4.7, "distance_km": 2.8, "phone": "+91-161-4000999", "has_emergency": True, "has_ambulance": True, "bed_count": 600, "address": "Ferozepur Road, Ludhiana"},
        {"name": "Deep Hospital", "location": "Ludhiana", "specialties": ["General Medicine", "Pediatrics", "Emergency"], "rating": 4.0, "distance_km": 1.8, "phone": "+91-161-5000666", "has_emergency": True, "has_ambulance": False, "bed_count": 120, "address": "Model Gram, Ludhiana"},
    ]
    for doc in hospitals:
        doc["createdAt"] = datetime.now(timezone.utc).isoformat()
    await col.insert_many(hospitals)


class HospitalRepository:
    async def find_all(
        self,
        location: Optional[str] = None,
        specialty: Optional[str] = None,
        emergency_only: bool = False,
        limit: int = 20,
    ) -> list[dict]:
        col = _get_collection()
        filters: dict = {}
        if location:
            filters["location"] = {"$regex": location, "$options": "i"}
        if specialty:
            filters["specialties"] = {"$regex": specialty, "$options": "i"}
        if emergency_only:
            filters["has_emergency"] = True
        cursor = col.find(filters).sort("rating", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def find_emergency(self, limit: int = 10) -> list[dict]:
        col = _get_collection()
        cursor = col.find({"has_emergency": True}).sort("rating", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_locations(self) -> list[str]:
        col = _get_collection()
        return await col.distinct("location")

    async def get_specialties(self) -> list[str]:
        col = _get_collection()
        return await col.distinct("specialties")

    async def count(self) -> int:
        col = _get_collection()
        return await col.count_documents({})
