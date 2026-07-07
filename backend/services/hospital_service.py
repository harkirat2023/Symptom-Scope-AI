from services.search_service import score_and_sort, filter_by_field
from services.disease_registry import get_specialist

HOSPITAL_DATABASE: list[dict] = [
    {
        "name": "Dayanand Medical College & Hospital",
        "location": "Ludhiana",
        "specialties": ["Cardiology", "Neurology", "Pulmonology", "General Medicine", "Emergency"],
        "rating": 4.6,
        "distance_km": 1.5,
        "phone": "+91-161-4688888",
        "has_emergency": True,
        "bed_count": 1200,
    },
    {
        "name": "Christian Medical College & Hospital",
        "location": "Ludhiana",
        "specialties": ["Cardiology", "Neurology", "Gastroenterology", "General Medicine", "Emergency", "Orthopedics"],
        "rating": 4.8,
        "distance_km": 3.0,
        "phone": "+91-161-5032255",
        "has_emergency": True,
        "bed_count": 1800,
    },
    {
        "name": "Fortis Hospital",
        "location": "Ludhiana",
        "specialties": ["Cardiology", "Neurology", "General Medicine", "Emergency"],
        "rating": 4.5,
        "distance_km": 4.2,
        "phone": "+91-161-4610100",
        "has_emergency": True,
        "bed_count": 350,
    },
    {
        "name": "Apollo Hospitals",
        "location": "Amritsar",
        "specialties": ["Cardiology", "Neurology", "Pulmonology", "Gastroenterology", "Emergency"],
        "rating": 4.7,
        "distance_km": 2.1,
        "phone": "+91-183-5088888",
        "has_emergency": True,
        "bed_count": 500,
    },
    {
        "name": "Surya Hospital",
        "location": "Amritsar",
        "specialties": ["General Medicine", "Pediatrics", "Orthopedics"],
        "rating": 4.2,
        "distance_km": 1.8,
        "phone": "+91-183-5012345",
        "has_emergency": True,
        "bed_count": 150,
    },
    {
        "name": "Patiala Government Medical College",
        "location": "Patiala",
        "specialties": ["General Medicine", "Cardiology", "Neurology", "Pulmonology", "Emergency"],
        "rating": 4.1,
        "distance_km": 2.5,
        "phone": "+91-175-3046000",
        "has_emergency": True,
        "bed_count": 900,
    },
    {
        "name": "Jalandhar Civil Hospital",
        "location": "Jalandhar",
        "specialties": ["General Medicine", "Pediatrics", "Emergency"],
        "rating": 3.8,
        "distance_km": 1.2,
        "phone": "+91-181-5012345",
        "has_emergency": True,
        "bed_count": 400,
    },
    {
        "name": "Shiv Hospital & Medical Centre",
        "location": "Jalandhar",
        "specialties": ["General Medicine", "Gastroenterology", "Orthopedics"],
        "rating": 4.0,
        "distance_km": 3.3,
        "phone": "+91-181-5078901",
        "has_emergency": False,
        "bed_count": 80,
    },
]

SPECIALTY_TO_DEPARTMENT: dict[str, str] = {
    "General Physician": "General Medicine",
    "Pulmonologist": "Pulmonology",
    "Cardiologist": "Cardiology",
    "Neurologist": "Neurology",
    "Gastroenterologist": "Gastroenterology",
    "Infectious Disease Specialist": "General Medicine",
    "Allergist": "General Medicine",
}


def _compute_hospital_score(
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

    if emergency_only:
        if hospital.get("has_emergency"):
            score += 0.15

    rating_score = hospital.get("rating", 0) / 5.0 * 0.10
    score += rating_score

    return min(score, 1.0)


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
    def search(
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
        results = list(HOSPITAL_DATABASE)

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
                search_fields=["name", "location", "specialties"],
                top_k=limit,
            )
            query_scores = {id(h): s for s, h in scored}
            results = [item for _, item in scored]

        if location:
            results = filter_by_field(results, "location", location)

        if specialty:
            mapped = SPECIALTY_TO_DEPARTMENT.get(specialty, specialty)
            results = [
                h for h in results
                if any(mapped.lower() in s.lower() for s in h["specialties"])
            ]

        if emergency_only:
            results = [h for h in results if h.get("has_emergency")]

        scored_hospitals = [
            (self._get_explainable_score(h, target_department, location, emergency_only), h)
            for h in results
        ]

        if query:
            max_qs = max(query_scores.values()) if query_scores else 1.0
            scored_hospitals = [
                (score + (query_scores.get(id(h), 0) / max_qs) * 0.20, h)
                for score, h in scored_hospitals
            ]

        scored_hospitals.sort(key=lambda x: (-x[0], -x[1].get("rating", 0)))
        ranked = [h for _, h in scored_hospitals]

        return ranked[:limit]

    def _get_explainable_score(
        self,
        hospital: dict,
        target_department: str | None,
        target_location: str | None,
        emergency_only: bool,
    ) -> float:
        return _compute_hospital_score(hospital, target_department, target_location, emergency_only)

    def explain_recommendation(self, hospital_name: str, disease: str | None = None) -> str:
        hospital = next(
            (h for h in HOSPITAL_DATABASE if h["name"].lower() == hospital_name.lower()),
            None,
        )
        if not hospital:
            return ""

        parts = [
            f"{hospital['name']} is located in {hospital['location']} "
            f"with a {hospital['rating']}/5 rating."
        ]

        if disease:
            expected_specialist = get_specialist(disease)
            department = SPECIALTY_TO_DEPARTMENT.get(expected_specialist, expected_specialist)
            has_dept = any(department.lower() in s.lower() for s in hospital["specialties"])
            if has_dept:
                parts.append(
                    f"It has a {department} department, which is the recommended specialty for {disease}."
                )
            else:
                parts.append(
                    f"It has departments in: {', '.join(hospital['specialties'])}."
                )

        if hospital.get("has_emergency"):
            parts.append("This hospital has an emergency department available 24/7.")

        parts.append(f"Contact: {hospital['phone']}.")
        return " ".join(parts)

    def get_locations(self) -> list[str]:
        seen: set[str] = set()
        return [l for l in (h["location"] for h in HOSPITAL_DATABASE) if not (l in seen or seen.add(l))]

    def get_specialties(self) -> list[str]:
        seen: set[str] = set()
        return [s for h in HOSPITAL_DATABASE for s in h["specialties"] if not (s in seen or seen.add(s))]
