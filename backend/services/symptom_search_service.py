from services.search_service import filter_by_field, score_and_sort

SYMPTOM_CATEGORIES: dict[str, str] = {
    "fever": "General",
    "dry_cough": "Respiratory",
    "fatigue": "General",
    "headache": "Neurological",
    "sore_throat": "Respiratory",
    "body_ache": "General",
    "chest_pain": "Cardiovascular",
    "shortness_of_breath": "Respiratory",
    "nausea": "Digestive",
    "vomiting": "Digestive",
    "diarrhea": "Digestive",
    "loss_of_taste": "Sensory",
    "loss_of_smell": "Sensory",
    "runny_nose": "Respiratory",
    "sneezing": "Respiratory",
    "joint_pain": "Musculoskeletal",
    "chills": "General",
    "sweating": "General",
    "dizziness": "Neurological",
    "abdominal_pain": "Digestive",
    "rash": "Dermatological",
    "muscle_weakness": "Musculoskeletal",
    "blurred_vision": "Neurological",
    "confusion": "Neurological",
    "seizure": "Neurological",
    "arm_pain": "Cardiovascular",
    "jaw_pain": "Cardiovascular",
    "facial_drooping": "Neurological",
    "speech_difficulty": "Neurological",
    "sensitivity_to_light": "Sensory",
    "sensitivity_to_sound": "Sensory",
}

SYMPTOM_DISPLAY_NAMES: dict[str, str] = {
    "dry_cough": "Dry Cough",
    "shortness_of_breath": "Shortness of Breath",
    "sore_throat": "Sore Throat",
    "body_ache": "Body Ache",
    "chest_pain": "Chest Pain",
    "runny_nose": "Runny Nose",
    "joint_pain": "Joint Pain",
    "abdominal_pain": "Abdominal Pain",
    "muscle_weakness": "Muscle Weakness",
    "blurred_vision": "Blurred Vision",
    "arm_pain": "Arm Pain",
    "jaw_pain": "Jaw Pain",
    "facial_drooping": "Facial Drooping",
    "speech_difficulty": "Speech Difficulty",
    "loss_of_taste": "Loss of Taste",
    "loss_of_smell": "Loss of Smell",
    "sensitivity_to_light": "Sensitivity to Light",
    "sensitivity_to_sound": "Sensitivity to Sound",
}


class SymptomSearchService:
    def __init__(self):
        self._symptoms = [
            {
                "id": name,
                "name": SYMPTOM_DISPLAY_NAMES.get(name, name.replace("_", " ").title()),
                "category": SYMPTOM_CATEGORIES.get(name, "Other"),
            }
            for name in sorted(SYMPTOM_CATEGORIES.keys())
        ]

    def search(
        self,
        query: str | None = None,
        category: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, str]]:
        results = [dict(s) for s in self._symptoms]

        if category:
            results = filter_by_field(results, "category", category)

        if query:
            scored = score_and_sort(
                results,
                query,
                search_fields=["name", "id"],
                top_k=limit,
            )
            results = [
                {**item, "relevance_score": round(score, 4)}
                for score, item in scored
            ]
        else:
            results = results[:limit]

        return results

    def get_categories(self) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for s in self._symptoms:
            cat = s["category"]
            if cat not in seen:
                seen.add(cat)
                ordered.append(cat)
        return ordered

    def get_by_category(self, category: str) -> list[dict[str, str]]:
        return [dict(s) for s in self._symptoms if s["category"].lower() == category.lower()]

    def get_all(self) -> list[dict[str, str]]:
        return [dict(s) for s in self._symptoms]
