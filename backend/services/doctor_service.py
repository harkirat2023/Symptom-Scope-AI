from schemas.doctor_schema import DoctorResponse
from services.search_service import score_and_sort, filter_by_field, compute_relevance
from services.disease_registry import get_specialist

DOCTOR_DATABASE: list[dict] = [
    {
        "name": "Dr. Sharma",
        "specialty": "General Physician",
        "location": "Ludhiana",
        "rating": 4.5,
        "distance_km": 2.3,
        "availability": "Today",
    },
    {
        "name": "Dr. Singh",
        "specialty": "Pulmonologist",
        "location": "Ludhiana",
        "rating": 4.8,
        "distance_km": 3.1,
        "availability": "Tomorrow",
    },
    {
        "name": "Dr. Patel",
        "specialty": "Cardiologist",
        "location": "Amritsar",
        "rating": 4.7,
        "distance_km": 5.0,
        "availability": "Today",
    },
    {
        "name": "Dr. Kaur",
        "specialty": "General Physician",
        "location": "Patiala",
        "rating": 4.3,
        "distance_km": 1.8,
        "availability": "Today",
    },
    {
        "name": "Dr. Verma",
        "specialty": "Neurologist",
        "location": "Jalandhar",
        "rating": 4.6,
        "distance_km": 4.2,
        "availability": "In 2 days",
    },
    {
        "name": "Dr. Gupta",
        "specialty": "Gastroenterologist",
        "location": "Ludhiana",
        "rating": 4.7,
        "distance_km": 2.8,
        "availability": "Today",
    },
    {
        "name": "Dr. Aggarwal",
        "specialty": "Infectious Disease Specialist",
        "location": "Amritsar",
        "rating": 4.6,
        "distance_km": 4.5,
        "availability": "Tomorrow",
    },
    {
        "name": "Dr. Kapoor",
        "specialty": "Allergist",
        "location": "Jalandhar",
        "rating": 4.4,
        "distance_km": 3.5,
        "availability": "In 2 days",
    },
]

AVAILABILITY_ORDER = {"Today": 0, "Tomorrow": 1, "In 2 days": 2}


class DoctorService:
    def get_recommendations(
        self,
        disease: str | None = None,
        specialty: str | None = None,
        location: str | None = None,
        query: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
        limit: int = 50,
    ) -> list[dict]:
        if not DOCTOR_DATABASE:
            return []

        results = list(DOCTOR_DATABASE)

        target_specialty = specialty
        if disease and not target_specialty:
            target_specialty = get_specialist(disease)

        if specialty:
            results = [d for d in results if specialty.lower() in d["specialty"].lower()]
        if location:
            results = [d for d in results if location.lower() in d["location"].lower()]

        scored_doctors: list[tuple[float, dict]] = []
        for doctor in results:
            specialty_score = 0.0
            location_score = 0.0
            rating_score = 0.0

            if target_specialty:
                specialty_score = compute_relevance(target_specialty, doctor["specialty"])

            if location:
                location_score = compute_relevance(location, doctor["location"])

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

        ranked = [doc for _, doc in scored_doctors]

        if location and not any(compute_relevance(location, d["location"]) > 0.5 for d in ranked[:5]):
            nearby = [d for d in ranked if compute_relevance(location, d["location"]) > 0.3]
            others = [d for d in ranked if d not in nearby]
            ranked = nearby + others

        return ranked[:limit]

    def get_specialty_for_disease(self, disease: str) -> str:
        return get_specialist(disease)

    def get_specialties(self) -> list[str]:
        seen: set[str] = set()
        return [s for s in (d["specialty"] for d in DOCTOR_DATABASE) if not (s in seen or seen.add(s))]

    def get_locations(self) -> list[str]:
        seen: set[str] = set()
        return [l for l in (d["location"] for d in DOCTOR_DATABASE) if not (l in seen or seen.add(l))]

    def explain_recommendation(self, doctor_name: str, disease: str | None = None) -> str:
        if not doctor_name or not doctor_name.strip():
            return ""
        doctor = next(
            (d for d in DOCTOR_DATABASE if d["name"].lower() == doctor_name.lower()),
            None,
        )
        if not doctor:
            return ""
        parts = [
            f"{doctor['name']} is a {doctor['specialty']} "
            f"located in {doctor['location']} with a {doctor['rating']}/5 rating."
        ]
        if disease:
            expected = self.get_specialty_for_disease(disease)
            match = "matches" if doctor["specialty"].lower() == expected.lower() else "is related to"
            parts.append(f"The recommended specialist for {disease} is {expected}, and {doctor['name']} {match} your condition.")
        availability = doctor.get("availability", "")
        if availability == "Today":
            parts.append("They are available today and can see you now.")
        elif availability:
            parts.append(f"They are available {availability.lower()}.")
        return " ".join(parts)
