"""MongoDB repository for doctor data."""

from datetime import datetime, timezone
from typing import Optional
from utils.database import get_database

_COLLECTION = None


def _get_collection():
    global _COLLECTION
    if _COLLECTION is None:
        _COLLECTION = get_database()["doctors"]
    return _COLLECTION


async def ensure_indexes():
    col = _get_collection()
    await col.create_index("specialty")
    await col.create_index("location")
    await col.create_index([("name", 1)], unique=True)


async def seed_doctors():
    """Seed the doctors collection with default data if empty."""
    col = _get_collection()
    existing = await col.count_documents({})
    if existing > 0:
        return

    doctors = [
        {"name": "Dr. Sharma", "specialty": "General Physician", "location": "Ludhiana", "rating": 4.5, "distance_km": 2.3, "availability": "Today", "phone": "+91-161-XXXXXXX", "hospital": "Dayanand Medical College", "experience_years": 15},
        {"name": "Dr. Singh", "specialty": "Pulmonologist", "location": "Ludhiana", "rating": 4.8, "distance_km": 3.1, "availability": "Tomorrow", "phone": "+91-161-XXXXXX1", "hospital": "CMC Ludhiana", "experience_years": 20},
        {"name": "Dr. Patel", "specialty": "Cardiologist", "location": "Amritsar", "rating": 4.7, "distance_km": 5.0, "availability": "Today", "phone": "+91-183-XXXXXXX", "hospital": "Apollo Amritsar", "experience_years": 18},
        {"name": "Dr. Kaur", "specialty": "General Physician", "location": "Patiala", "rating": 4.3, "distance_km": 1.8, "availability": "Today", "phone": "+91-175-XXXXXXX", "hospital": "Govt Medical College Patiala", "experience_years": 12},
        {"name": "Dr. Verma", "specialty": "Neurologist", "location": "Jalandhar", "rating": 4.6, "distance_km": 4.2, "availability": "In 2 days", "phone": "+91-181-XXXXXXX", "hospital": "Jalandhar Civil Hospital", "experience_years": 16},
        {"name": "Dr. Gupta", "specialty": "Gastroenterologist", "location": "Ludhiana", "rating": 4.7, "distance_km": 2.8, "availability": "Today", "phone": "+91-161-XXXXXX2", "hospital": "Fortis Ludhiana", "experience_years": 14},
        {"name": "Dr. Aggarwal", "specialty": "Infectious Disease Specialist", "location": "Amritsar", "rating": 4.6, "distance_km": 4.5, "availability": "Tomorrow", "phone": "+91-183-XXXXXX1", "hospital": "Apollo Amritsar", "experience_years": 22},
        {"name": "Dr. Kapoor", "specialty": "Allergist", "location": "Jalandhar", "rating": 4.4, "distance_km": 3.5, "availability": "In 2 days", "phone": "+91-181-XXXXXX1", "hospital": "Shiv Hospital Jalandhar", "experience_years": 10},
        {"name": "Dr. Bhatia", "specialty": "General Physician", "location": "Ludhiana", "rating": 4.2, "distance_km": 1.0, "availability": "Today", "phone": "+91-161-XXXXXX3", "hospital": "SPS Apollo", "experience_years": 8},
        {"name": "Dr. Malhotra", "specialty": "Pulmonologist", "location": "Amritsar", "rating": 4.5, "distance_km": 3.8, "availability": "Tomorrow", "phone": "+91-183-XXXXXX2", "hospital": "Surya Hospital", "experience_years": 13},
        {"name": "Dr. Mehta", "specialty": "Cardiologist", "location": "Ludhiana", "rating": 4.9, "distance_km": 2.0, "availability": "Today", "phone": "+91-161-XXXXXX4", "hospital": "Dayanand Medical College", "experience_years": 25},
        {"name": "Dr. Joshi", "specialty": "Neurologist", "location": "Patiala", "rating": 4.4, "distance_km": 3.2, "availability": "In 2 days", "phone": "+91-175-XXXXXX1", "hospital": "Rajindra Hospital", "experience_years": 11},
        {"name": "Dr. Chawla", "specialty": "Gastroenterologist", "location": "Jalandhar", "rating": 4.3, "distance_km": 2.7, "availability": "Today", "phone": "+91-181-XXXXXX2", "hospital": "Jalandhar Civil Hospital", "experience_years": 9},
        {"name": "Dr. Nair", "specialty": "Infectious Disease Specialist", "location": "Ludhiana", "rating": 4.7, "distance_km": 3.5, "availability": "Today", "phone": "+91-161-XXXXXX5", "hospital": "CMC Ludhiana", "experience_years": 19},
        {"name": "Dr. Arora", "specialty": "General Physician", "location": "Amritsar", "rating": 4.1, "distance_km": 1.2, "availability": "Today", "phone": "+91-183-XXXXXX3", "hospital": "Surya Hospital", "experience_years": 7},
    ]
    for doc in doctors:
        doc["createdAt"] = datetime.now(timezone.utc).isoformat()
    await col.insert_many(doctors)


class DoctorRepository:
    async def find_all(
        self,
        specialty: Optional[str] = None,
        location: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        col = _get_collection()
        filters: dict = {}
        if specialty:
            filters["specialty"] = {"$regex": specialty, "$options": "i"}
        if location:
            filters["location"] = {"$regex": location, "$options": "i"}
        cursor = col.find(filters).limit(limit)
        return await cursor.to_list(length=limit)

    async def find_by_specialty(self, specialty: str, limit: int = 10) -> list[dict]:
        col = _get_collection()
        cursor = col.find({"specialty": {"$regex": specialty, "$options": "i"}}).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_specialties(self) -> list[str]:
        col = _get_collection()
        return await col.distinct("specialty")

    async def get_locations(self) -> list[str]:
        col = _get_collection()
        return await col.distinct("location")

    async def count(self) -> int:
        col = _get_collection()
        return await col.count_documents({})
