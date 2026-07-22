"""Hospital service — now backed by MongoDB repository."""

from services.search_service import score_and_sort, filter_by_field
from services.disease_registry import get_specialist
from repositories.hospital_repository import HospitalRepository

SPECIALTY_TO_DEPARTMENT: dict[str, str] = {
    "General Physician": "General Medicine",
    "Pulmonologist": "Pulmonology",
    "Cardiologist": "Cardiology",
    "Neurologist": "Neurology",
    "Gastroenterologist": "Gastroenterology",
    "Infectious Disease Specialist": "General Medicine",
    "Allergist": "General Medicine",
}


def _compute_text_relevance(query: str, text: str) -> float:
    q = query.lower().strip()
    t = text.lower().strip()
    if not q or not t:
        return 0.0
    if q == t:
        return 1.0
    if q in t:
        return 0.8
    if t in q:
        return 0.6
    return 0.0


class HospitalService:
    def __init__(self):
        self._repo = HospitalRepository()

    async def search(
        self,
        query: str | None = None,
        location: str | None = None,
        specialty: str | None = None,
        disease: str | None = None,
        emergency_only: bool = False,
        sort_by: str | None = None,
        sort_order: str = "desc",
        limit: int = 20,
    ) -> list[dict]:
        results = await self._repo.find_all(
            location=location,
            specialty=specialty,
            emergency_only=emergency_only,
            limit=limit * 3,
        )

        if not results:
            return []

        target_department = None
        if specialty:
            target_department = SPECIALTY_TO_DEPARTMENT.get(specialty, specialty)
        elif disease:
            disease_specialist = get_specialist(disease)
            target_department = SPECIALTY_TO_DEPARTMENT.get(disease_specialist, disease_specialist)

        query_scores: dict[int, float] = {}
        if query:
            scored = score_and_sort(
                results, query,
                search_fields=["name", "location"],
                top_k=limit,
            )
            query_scores = {id(h): s for s, h in scored}
            results = [item for _, item in scored]

        scored_hospitals = [
            (self._compute_score(h, target_department, location, emergency_only), h)
            for h in results
        ]

        if query and query_scores:
            max_qs = max(query_scores.values()) if query_scores else 1.0
            scored_hospitals = [
                (score + (query_scores.get(id(h), 0) / max_qs) * 0.20, h)
                for score, h in scored_hospitals
            ]

        reverse = sort_order == "desc"
        if sort_by == "rating":
            scored_hospitals.sort(key=lambda x: x[1].get("rating", 0), reverse=reverse)
        elif sort_by == "distance_km":
            scored_hospitals.sort(key=lambda x: x[1].get("distance_km", 0), reverse=reverse)
        else:
            scored_hospitals.sort(key=lambda x: (-x[0], -x[1].get("rating", 0)))

        ranked = [self._serialize(h) for _, h in scored_hospitals]
        return ranked[:limit]

    @staticmethod
    def _compute_score(
        hospital: dict,
        target_department: str | None,
        target_location: str | None,
        emergency_only: bool,
    ) -> float:
        score = 0.0
        if target_department:
            department_match = any(
                target_department.lower() in s.lower() for s in hospital.get("specialties", [])
            )
            if department_match:
                score += 0.50
            else:
                general_match = any(
                    "general medicine" in s.lower() for s in hospital.get("specialties", [])
                )
                if general_match:
                    score += 0.25
        if target_location:
            location_match = target_location.lower() in hospital.get("location", "").lower()
            if location_match:
                score += 0.25
            else:
                loc_score = _compute_text_relevance(target_location, hospital.get("location", ""))
                score += loc_score * 0.15
        if emergency_only and hospital.get("has_emergency"):
            score += 0.15
        rating_score = hospital.get("rating", 0) / 5.0 * 0.10
        score += rating_score
        return min(score, 1.0)

    async def get_locations(self) -> list[str]:
        return await self._repo.get_locations()

    async def get_specialties(self) -> list[str]:
        return await self._repo.get_specialties()

    def explain_recommendation(self, hospital_name: str, disease: str | None = None) -> str:
        parts = [f"{hospital_name} is a recommended healthcare facility."]
        if disease:
            expected_specialist = get_specialist(disease)
            department = SPECIALTY_TO_DEPARTMENT.get(expected_specialist, expected_specialist)
            parts.append(f"The recommended department for {disease} is {department}.")
        return " ".join(parts)

    @staticmethod
    def _serialize(doc: dict) -> dict:
        return {
            "name": doc.get("name", ""),
            "location": doc.get("location", ""),
            "specialties": doc.get("specialties", []),
            "rating": float(doc.get("rating", 0)),
            "distance_km": float(doc.get("distance_km", 0)),
            "phone": doc.get("phone", ""),
            "emergency": bool(doc.get("has_emergency", False)),
            "has_ambulance": bool(doc.get("has_ambulance", False)),
            "bed_count": int(doc.get("bed_count", 0)),
            "address": doc.get("address", ""),
        }
