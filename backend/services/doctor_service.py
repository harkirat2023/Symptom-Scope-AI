"""Doctor service — now backed by MongoDB repository."""

from repositories.doctor_repository import DoctorRepository
from services.disease_registry import get_specialist
from services.search_service import compute_relevance

AVAILABILITY_ORDER = {"Today": 0, "Tomorrow": 1, "In 2 days": 2}


class DoctorService:
    def __init__(self):
        self._repo = DoctorRepository()

    async def get_recommendations(
        self,
        disease: str | None = None,
        specialty: str | None = None,
        location: str | None = None,
        query: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
        limit: int = 50,
    ) -> list[dict]:
        doctors = await self._repo.find_all(
            specialty=specialty,
            location=location,
            query=query,
            limit=limit * 3,
        )

        if not doctors:
            return []

        target_specialty = specialty
        if disease and not target_specialty:
            target_specialty = get_specialist(disease)

        scored_doctors: list[tuple[float, dict]] = []
        for doctor in doctors:
            specialty_score = 0.0
            location_score = 0.0
            rating_score = 0.0

            if target_specialty:
                specialty_score = compute_relevance(target_specialty, doctor.get("specialty", ""))

            if location:
                location_score = compute_relevance(location, doctor.get("location", ""))

            rating_score = doctor.get("rating", 0) / 5.0

            if query:
                query_score = max(
                    compute_relevance(query, str(doctor.get(f, "")))
                    for f in ["name", "specialty", "location"]
                )
            else:
                query_score = 0.5

            composite = (
                specialty_score * 0.50
                + location_score * 0.25
                + rating_score * 0.15
                + query_score * 0.10
            )

            scored_doctors.append((composite, doctor))

        if sort_by == "rating":
            reverse = sort_order == "desc"
            scored_doctors.sort(key=lambda x: x[1].get("rating", 0), reverse=reverse)
        elif sort_by == "distance_km":
            reverse = sort_order == "desc"
            scored_doctors.sort(key=lambda x: x[1].get("distance_km", 0), reverse=reverse)
        elif sort_by == "availability":
            reverse = sort_order == "desc"
            scored_doctors.sort(
                key=lambda x: AVAILABILITY_ORDER.get(x[1].get("availability", ""), 99),
                reverse=reverse,
            )
        else:
            scored_doctors.sort(key=lambda x: (-x[0], x[1].get("rating", 0)))

        ranked = [self._serialize(doc) for _, doc in scored_doctors]

        if location and not any(compute_relevance(location, d["location"]) > 0.5 for d in ranked[:5]):
            nearby = [d for d in ranked if compute_relevance(location, d["location"]) > 0.3]
            others = [d for d in ranked if d not in nearby]
            ranked = nearby + others

        return ranked[:limit]

    async def get_specialty_for_disease(self, disease: str) -> str:
        return get_specialist(disease)

    async def get_specialties(self) -> list[str]:
        return await self._repo.get_specialties()

    async def get_locations(self) -> list[str]:
        return await self._repo.get_locations()

    async def explain_recommendation(self, doctor_name: str, disease: str | None = None) -> str:
        if not doctor_name or not doctor_name.strip():
            return ""
        parts = [
            f"{doctor_name} is a recommended healthcare professional."
        ]
        if disease:
            expected = await self.get_specialty_for_disease(disease)
            parts.append(f"The recommended specialist for {disease} is {expected}.")
        return " ".join(parts)

    @staticmethod
    def _serialize(doc: dict) -> dict:
        return {
            "name": doc.get("name", ""),
            "specialty": doc.get("specialty", ""),
            "location": doc.get("location", ""),
            "rating": float(doc.get("rating", 0)),
            "distance_km": float(doc.get("distance_km", 0)),
            "availability": doc.get("availability") if isinstance(doc.get("availability"), list) else [doc.get("availability", "")] if doc.get("availability") else [],
            "phone": doc.get("phone", ""),
            "hospital": doc.get("hospital", ""),
            "experience_years": int(doc.get("experience_years", 0)),
        }
