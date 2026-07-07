from dataclasses import dataclass, field


@dataclass
class Precaution:
    text: str
    priority: int


@dataclass
class DiseaseMetadata:
    name: str
    severity: str
    specialist: str
    precautions: list[Precaution]
    symptom_pattern: list[str]
    description: str
    emergency_risk: bool
    escalation_severity: str | None = None
    escalation_threshold: float | None = None


DISEASE_REGISTRY: dict[str, DiseaseMetadata] = {
    "Common Cold": DiseaseMetadata(
        name="Common Cold",
        severity="Mild",
        specialist="General Physician",
        symptom_pattern=["runny_nose", "sneezing", "sore_throat", "dry_cough", "headache", "fatigue"],
        description=(
            "The common cold is a viral infection of the upper respiratory tract. "
            "It is usually harmless and self-limiting, with symptoms typically resolving within 7–10 days."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Rest and stay hydrated with warm fluids", priority=1),
            Precaution("Use over-the-counter cold medication for symptom relief", priority=2),
            Precaution("Gargle with warm salt water to soothe sore throat", priority=3),
            Precaution("Use a humidifier for nasal congestion relief", priority=4),
            Precaution("Seek medical attention if fever lasts more than 3 days or symptoms worsen", priority=5),
        ],
    ),
    "Allergy": DiseaseMetadata(
        name="Allergy",
        severity="Mild",
        specialist="Allergist",
        symptom_pattern=["sneezing", "runny_nose", "rash", "headache", "fatigue"],
        description=(
            "Allergies occur when the immune system reacts to a foreign substance such as pollen, "
            "pet dander, or food. Symptoms are typically mild and manageable with antihistamines."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Take oral antihistamine (cetirizine/loratadine) for symptom relief", priority=1),
            Precaution("Avoid known allergens and triggers", priority=2),
            Precaution("Apply cold compress to reduce swelling and itching", priority=3),
            Precaution("Use topical hydrocortisone cream for localized skin reactions", priority=4),
            Precaution("Seek emergency care if experiencing facial swelling or difficulty breathing", priority=5),
        ],
    ),
    "Mild Food Poisoning": DiseaseMetadata(
        name="Mild Food Poisoning",
        severity="Mild",
        specialist="Gastroenterologist",
        symptom_pattern=["nausea", "vomiting", "diarrhea", "abdominal_pain", "fatigue"],
        description=(
            "Food poisoning is caused by consuming contaminated food or water. "
            "Mild cases resolve with rest and hydration within 24–48 hours."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Stay hydrated with ORS solution or clear fluids", priority=1),
            Precaution("Rest and avoid solid foods until vomiting/diarrhea subsides", priority=2),
            Precaution("Follow BRAT diet (bananas, rice, applesauce, toast) when reintroducing food", priority=3),
            Precaution("Avoid dairy, caffeine, and fatty foods for 48 hours after recovery", priority=4),
            Precaution("Seek medical attention if symptoms persist beyond 48 hours or blood appears in stool", priority=5),
        ],
    ),
    "Influenza": DiseaseMetadata(
        name="Influenza",
        severity="Moderate",
        specialist="General Physician",
        symptom_pattern=["fever", "dry_cough", "fatigue", "headache", "body_ache", "sore_throat", "chills", "runny_nose"],
        description=(
            "Influenza (flu) is a contagious respiratory illness caused by influenza viruses. "
            "It can cause mild to severe illness and may lead to complications like pneumonia."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Rest adequately and avoid strenuous activity", priority=1),
            Precaution("Drink plenty of fluids to prevent dehydration", priority=2),
            Precaution("Monitor temperature; use antipyretics if fever exceeds 101°F", priority=3),
            Precaution("Visit physician if symptoms worsen or persist beyond 5 days", priority=4),
            Precaution("Seek emergency care if breathing becomes difficult", priority=5),
        ],
    ),
    "Bronchitis": DiseaseMetadata(
        name="Bronchitis",
        severity="Moderate",
        specialist="Pulmonologist",
        symptom_pattern=["dry_cough", "fatigue", "chest_pain", "fever", "shortness_of_breath", "body_ache"],
        description=(
            "Bronchitis is inflammation of the bronchial tubes, usually caused by viral infections. "
            "It is characterized by cough with mucus, chest discomfort, and fatigue."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Rest and stay hydrated to thin mucus secretions", priority=1),
            Precaution("Use cough suppressant only for dry, non-productive cough", priority=2),
            Precaution("Avoid smoke, dust, and other respiratory irritants", priority=3),
            Precaution("Use steam inhalation or humidifier to relieve congestion", priority=4),
            Precaution("Consult physician if cough persists beyond 3 weeks or produces blood", priority=5),
        ],
    ),
    "Gastroenteritis": DiseaseMetadata(
        name="Gastroenteritis",
        severity="Moderate",
        specialist="Gastroenterologist",
        symptom_pattern=["nausea", "vomiting", "diarrhea", "abdominal_pain", "fever", "fatigue", "body_ache"],
        description=(
            "Gastroenteritis is inflammation of the stomach and intestines, commonly caused by viral "
            "or bacterial infections. It typically resolves within a few days with supportive care."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Stay hydrated with ORS solution or electrolyte drinks", priority=1),
            Precaution("Follow BRAT diet (bananas, rice, applesauce, toast) when able to eat", priority=2),
            Precaution("Avoid dairy, caffeine, alcohol, and spicy foods until recovery", priority=3),
            Precaution("Wash hands thoroughly and frequently to prevent spread", priority=4),
            Precaution("Seek medical attention if unable to keep fluids down for 24 hours", priority=5),
        ],
    ),
    "Migraine": DiseaseMetadata(
        name="Migraine",
        severity="Moderate",
        specialist="Neurologist",
        symptom_pattern=[
            "headache", "nausea", "vomiting", "blurred_vision", "dizziness", "fatigue",
            "sensitivity_to_light", "sensitivity_to_sound",
        ],
        description=(
            "Migraine is a neurological condition characterized by intense, debilitating headaches "
            "often accompanied by nausea, vomiting, and sensitivity to light and sound."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Rest in a dark, quiet room without screen exposure", priority=1),
            Precaution("Apply cold compress to forehead or temples", priority=2),
            Precaution("Take prescribed triptan or NSAID at onset of symptoms", priority=3),
            Precaution("Avoid bright lights, loud noises, and strong odors", priority=4),
            Precaution("Consult neurologist if migraines occur more than 4 times per month", priority=5),
        ],
    ),
    "Pneumonia": DiseaseMetadata(
        name="Pneumonia",
        severity="Severe",
        specialist="Pulmonologist",
        symptom_pattern=["fever", "dry_cough", "fatigue", "shortness_of_breath", "chest_pain", "chills", "sweating", "body_ache"],
        description=(
            "Pneumonia is an infection that inflames the air sacs in one or both lungs. "
            "It can range from mild to life-threatening and requires prompt medical attention."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Seek immediate medical attention — pneumonia requires urgent care", priority=1),
            Precaution("Complete prescribed antibiotic course even if symptoms improve", priority=2),
            Precaution("Rest and avoid all physical exertion until cleared by physician", priority=3),
            Precaution("Monitor oxygen levels with pulse oximeter if available", priority=4),
            Precaution("Return to ER if breathing worsens or chest pain increases", priority=5),
        ],
    ),
    "Heart Attack": DiseaseMetadata(
        name="Heart Attack",
        severity="Severe",
        specialist="Cardiologist",
        symptom_pattern=["chest_pain", "shortness_of_breath", "nausea", "sweating", "dizziness", "fatigue", "arm_pain", "jaw_pain"],
        description=(
            "A heart attack (myocardial infarction) occurs when blood flow to the heart is severely "
            "reduced or blocked. It is a life-threatening medical emergency requiring immediate intervention."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Call emergency services (108/911) immediately — do not delay", priority=1),
            Precaution("Chew 325 mg aspirin if not allergic while waiting for help", priority=2),
            Precaution("Stay calm, sit down, and rest in a comfortable position", priority=3),
            Precaution("Do not drive yourself to the hospital", priority=4),
            Precaution("If unconscious, begin CPR until paramedics arrive", priority=5),
        ],
    ),
    "Stroke": DiseaseMetadata(
        name="Stroke",
        severity="Severe",
        specialist="Neurologist",
        symptom_pattern=[
            "confusion", "blurred_vision", "headache", "dizziness", "muscle_weakness",
            "fatigue", "facial_drooping", "speech_difficulty",
        ],
        description=(
            "A stroke occurs when blood supply to part of the brain is interrupted or reduced. "
            "Time-critical emergency — early treatment significantly improves outcomes."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Call emergency services (108/911) immediately", priority=1),
            Precaution("Note the exact time symptoms first appeared", priority=2),
            Precaution("Keep patient calm, lying flat on their side if unconscious", priority=3),
            Precaution("Do not give any food, water, or medication by mouth", priority=4),
            Precaution("Rapid treatment (within 4.5 hours) improves outcomes significantly", priority=5),
        ],
    ),
    "Severe Respiratory Distress": DiseaseMetadata(
        name="Severe Respiratory Distress",
        severity="Severe",
        specialist="Pulmonologist",
        symptom_pattern=["shortness_of_breath", "chest_pain", "dry_cough", "confusion", "fatigue", "fever"],
        description=(
            "Severe respiratory distress is a life-threatening condition where the lungs cannot "
            "provide enough oxygen to the body. Immediate emergency care is required."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Call emergency services (108/911) immediately", priority=1),
            Precaution("Sit upright and lean forward slightly to optimize breathing", priority=2),
            Precaution("Do not lie flat — this worsens respiratory effort", priority=3),
            Precaution("Use prescribed rescue inhaler (e.g., albuterol) if available", priority=4),
            Precaution("Loosen tight clothing around neck and chest while waiting for help", priority=5),
        ],
    ),
    "Malaria": DiseaseMetadata(
        name="Malaria",
        severity="Severe",
        specialist="Infectious Disease Specialist",
        symptom_pattern=["fever", "chills", "sweating", "headache", "body_ache", "fatigue", "nausea", "vomiting"],
        description=(
            "Malaria is a life-threatening disease caused by parasites transmitted through "
            "the bite of infected mosquitoes. Early treatment is critical."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Seek immediate medical treatment — malaria can progress rapidly", priority=1),
            Precaution("Complete full course of antimalarial medication as prescribed", priority=2),
            Precaution("Use insecticide-treated mosquito nets while sleeping", priority=3),
            Precaution("Apply EPA-registered mosquito repellent during outdoor activity", priority=4),
            Precaution("Monitor fever patterns and return to hospital if fever recurs", priority=5),
        ],
    ),
    "Dengue": DiseaseMetadata(
        name="Dengue",
        severity="Severe",
        specialist="Infectious Disease Specialist",
        symptom_pattern=["fever", "headache", "body_ache", "joint_pain", "rash", "nausea", "vomiting", "fatigue"],
        description=(
            "Dengue is a mosquito-borne viral infection causing flu-like symptoms. "
            "Severe dengue can be life-threatening and requires medical monitoring."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Seek medical care immediately for proper monitoring", priority=1),
            Precaution("Stay hydrated with oral fluids; IV fluids may be needed", priority=2),
            Precaution("Monitor platelet counts and watch for bleeding gums or nose", priority=3),
            Precaution("Avoid NSAIDs (ibuprofen, aspirin) — use paracetamol for fever", priority=4),
            Precaution("Return to ER immediately if experiencing severe abdominal pain or vomiting blood", priority=5),
        ],
    ),
    "COVID-19": DiseaseMetadata(
        name="COVID-19",
        severity="Moderate",
        specialist="Pulmonologist",
        symptom_pattern=[
            "fever", "dry_cough", "fatigue", "loss_of_taste", "loss_of_smell",
            "headache", "sore_throat", "shortness_of_breath", "body_ache",
        ],
        description=(
            "COVID-19 is a respiratory illness caused by the SARS-CoV-2 virus. "
            "Most cases are mild to moderate, but severe complications can occur."
        ),
        emergency_risk=True,
        escalation_severity="Severe",
        escalation_threshold=85.0,
        precautions=[
            Precaution("Isolate immediately to prevent spread to others", priority=1),
            Precaution("Monitor oxygen levels with pulse oximeter — seek help if below 94%", priority=2),
            Precaution("Stay hydrated and rest; use antipyretics for fever", priority=3),
            Precaution("Track symptom progression daily; seek care if breathing worsens", priority=4),
            Precaution("Seek emergency care for persistent chest pain, confusion, or bluish lips", priority=5),
        ],
    ),
    "Epilepsy": DiseaseMetadata(
        name="Epilepsy",
        severity="Severe",
        specialist="Neurologist",
        symptom_pattern=["seizure", "confusion", "fatigue", "headache", "muscle_weakness", "dizziness"],
        description=(
            "Epilepsy is a neurological disorder characterized by recurrent seizures. "
            "Seizures vary in intensity and duration; prolonged seizures require emergency care."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Ensure airway is clear and gently turn person onto their side (recovery position)", priority=1),
            Precaution("Do not restrain the person or put anything in their mouth", priority=2),
            Precaution("Time the seizure duration — call emergency services if more than 5 minutes", priority=3),
            Precaution("Remove nearby sharp or hard objects to prevent injury", priority=4),
            Precaution("Stay with the person until they are fully conscious and oriented", priority=5),
        ],
    ),
}


SEVERITY_ORDER = {"Mild": 1, "Moderate": 2, "Severe": 3}


def get_disease(name: str) -> DiseaseMetadata | None:
    return DISEASE_REGISTRY.get(name)


def get_severity(name: str) -> str:
    disease = DISEASE_REGISTRY.get(name)
    if disease is None:
        return "Moderate"
    return disease.severity


def get_specialist(name: str) -> str:
    disease = DISEASE_REGISTRY.get(name)
    if disease is None:
        return "General Physician"
    return disease.specialist


def get_precautions(name: str) -> list[Precaution]:
    disease = DISEASE_REGISTRY.get(name)
    if disease is None:
        return []
    return disease.precautions


def is_emergency_risk(name: str) -> bool:
    disease = DISEASE_REGISTRY.get(name)
    if disease is None:
        return False
    return disease.emergency_risk


def get_escalation(name: str) -> tuple[str | None, float | None]:
    disease = DISEASE_REGISTRY.get(name)
    if disease is None:
        return None, None
    return disease.escalation_severity, disease.escalation_threshold


FALLBACK_PRECAUTIONS_BY_SEVERITY: dict[str, list[Precaution]] = {
    "Mild": [
        Precaution("Rest and monitor your symptoms", priority=1),
        Precaution("Stay hydrated and maintain a balanced diet", priority=2),
        Precaution("Use over-the-counter remedies as appropriate", priority=3),
        Precaution("Consult a healthcare professional if symptoms worsen", priority=4),
    ],
    "Moderate": [
        Precaution("Schedule an appointment with a healthcare provider", priority=1),
        Precaution("Monitor symptom progression closely", priority=2),
        Precaution("Avoid strenuous activity until evaluated", priority=3),
        Precaution("Seek immediate care if symptoms suddenly worsen", priority=4),
    ],
    "Severe": [
        Precaution("Seek immediate medical attention — this condition requires urgent evaluation", priority=1),
        Precaution("Do not delay treatment; visit the nearest emergency department", priority=2),
        Precaution("Arrange transportation — do not drive yourself", priority=3),
        Precaution("Have a caregiver or family member accompany you if possible", priority=4),
    ],
}
