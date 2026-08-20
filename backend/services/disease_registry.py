"""
services.disease_registry
==========================
Canonical metadata for every disease the SymptomScope AI system can predict.

Covers all 24 diseases from the Symptom2Disease Kaggle dataset plus
5 emergency/rare diseases (Heart Attack, Stroke, Epilepsy, COVID-19,
Severe Respiratory Distress) from the training augmentation set.
"""

from dataclasses import dataclass


@dataclass
class Precaution:
    text: str
    priority: int


@dataclass
class DiseaseMetadata:
    name: str
    severity: str          # "Mild" | "Moderate" | "Severe"
    specialist: str
    precautions: list[Precaution]
    symptom_pattern: list[str]
    description: str
    emergency_risk: bool
    escalation_severity: str | None = None
    escalation_threshold: float | None = None


DISEASE_REGISTRY: dict[str, DiseaseMetadata] = {

    # ------------------------------------------------------------------ #
    #  MILD DISEASES                                                       #
    # ------------------------------------------------------------------ #

    "Common Cold": DiseaseMetadata(
        name="Common Cold",
        severity="Mild",
        specialist="General Physician",
        symptom_pattern=["runny_nose", "sneezing", "sore_throat", "cough", "headache", "fatigue"],
        description=(
            "The common cold is a viral infection of the upper respiratory tract. "
            "It is usually harmless and self-limiting, resolving within 7–10 days."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Rest and stay hydrated with warm fluids", priority=1),
            Precaution("Use OTC cold medication for symptom relief", priority=2),
            Precaution("Gargle with warm salt water to soothe sore throat", priority=3),
            Precaution("Use a humidifier for nasal congestion relief", priority=4),
            Precaution("Seek medical attention if fever lasts more than 3 days", priority=5),
        ],
    ),

    "Allergy": DiseaseMetadata(
        name="Allergy",
        severity="Mild",
        specialist="Allergist",
        symptom_pattern=["sneezing", "runny_nose", "rash", "headache", "fatigue", "watering_from_eyes"],
        description=(
            "Allergies occur when the immune system overreacts to a foreign substance "
            "such as pollen, pet dander, or food. Symptoms are typically mild and manageable."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Take oral antihistamine (cetirizine/loratadine) for relief", priority=1),
            Precaution("Avoid known allergens and triggers", priority=2),
            Precaution("Apply cold compress to reduce swelling and itching", priority=3),
            Precaution("Use topical hydrocortisone cream for localized skin reactions", priority=4),
            Precaution("Seek emergency care for facial swelling or difficulty breathing", priority=5),
        ],
    ),

    "Acne": DiseaseMetadata(
        name="Acne",
        severity="Mild",
        specialist="Dermatologist",
        symptom_pattern=["skin_rash", "pus_filled_pimples", "blackheads", "scurring"],
        description=(
            "Acne is a common skin condition that occurs when hair follicles become plugged "
            "with oil and dead skin cells, causing pimples and blackheads."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Wash face gently twice daily with mild cleanser", priority=1),
            Precaution("Avoid squeezing or popping pimples", priority=2),
            Precaution("Use non-comedogenic moisturizer and sunscreen", priority=3),
            Precaution("Consult a dermatologist for persistent or severe acne", priority=4),
            Precaution("Avoid touching face frequently to prevent bacteria spread", priority=5),
        ],
    ),

    "Fungal Infection": DiseaseMetadata(
        name="Fungal Infection",
        severity="Mild",
        specialist="Dermatologist",
        symptom_pattern=["itching", "skin_rash", "dischromic_patches", "nodal_skin_eruptions"],
        description=(
            "Fungal infections of the skin are caused by dermatophytes or yeasts. "
            "They produce itchy rashes and discoloured skin patches."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Keep affected area clean and dry", priority=1),
            Precaution("Apply antifungal cream or powder as directed", priority=2),
            Precaution("Wear loose, breathable cotton clothing", priority=3),
            Precaution("Avoid sharing towels or personal items", priority=4),
            Precaution("Complete the full antifungal course even after symptoms clear", priority=5),
        ],
    ),

    "Impetigo": DiseaseMetadata(
        name="Impetigo",
        severity="Mild",
        specialist="Dermatologist",
        symptom_pattern=["skin_rash", "itching", "fatigue", "high_fever", "blister",
                         "red_sore_around_nose", "yellow_crust_ooze"],
        description=(
            "Impetigo is a highly contagious bacterial skin infection causing red sores "
            "that rupture, ooze, and form yellowish crusts."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Keep sores clean and covered with a loose bandage", priority=1),
            Precaution("Apply prescribed antibiotic cream to affected areas", priority=2),
            Precaution("Wash hands frequently to prevent spread", priority=3),
            Precaution("Avoid sharing personal items such as towels or razors", priority=4),
            Precaution("Consult a doctor if sores spread or do not improve in 3 days", priority=5),
        ],
    ),

    "Drug Reaction": DiseaseMetadata(
        name="Drug Reaction",
        severity="Mild",
        specialist="General Physician",
        symptom_pattern=["itching", "skin_rash", "stomach_pain", "vomiting", "burning_micturition"],
        description=(
            "A drug reaction is an unwanted effect caused by a medication. "
            "Reactions range from mild rashes to life-threatening anaphylaxis."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Stop taking the suspected medication immediately", priority=1),
            Precaution("Consult your doctor before stopping any prescribed medication", priority=2),
            Precaution("Apply antihistamine cream for skin rash if mild", priority=3),
            Precaution("Stay hydrated and rest", priority=4),
            Precaution("Seek emergency care for throat swelling or difficulty breathing", priority=5),
        ],
    ),

    "Urinary Tract Infection": DiseaseMetadata(
        name="Urinary Tract Infection",
        severity="Mild",
        specialist="Urologist",
        symptom_pattern=["burning_micturition", "bladder_discomfort", "foul_smell_of_urine",
                         "continuous_feel_of_urine"],
        description=(
            "A urinary tract infection (UTI) is a bacterial infection that affects any part "
            "of the urinary system. It is more common in women."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Drink plenty of water to flush bacteria", priority=1),
            Precaution("Complete the full course of prescribed antibiotics", priority=2),
            Precaution("Avoid holding urine for extended periods", priority=3),
            Precaution("Use unsweetened cranberry products if tolerated", priority=4),
            Precaution("Seek medical care if fever or back pain develops", priority=5),
        ],
    ),

    # ------------------------------------------------------------------ #
    #  MODERATE DISEASES                                                   #
    # ------------------------------------------------------------------ #

    "Influenza": DiseaseMetadata(
        name="Influenza",
        severity="Moderate",
        specialist="General Physician",
        symptom_pattern=["fever", "cough", "fatigue", "headache", "body_ache", "sore_throat", "chills"],
        description=(
            "Influenza (flu) is a contagious respiratory illness caused by influenza viruses. "
            "It can cause mild to severe illness and may lead to complications like pneumonia."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Rest and avoid strenuous activity", priority=1),
            Precaution("Drink plenty of fluids to prevent dehydration", priority=2),
            Precaution("Use antipyretics if fever exceeds 101°F", priority=3),
            Precaution("Visit physician if symptoms worsen or persist beyond 5 days", priority=4),
            Precaution("Seek emergency care if breathing becomes difficult", priority=5),
        ],
    ),

    "Migraine": DiseaseMetadata(
        name="Migraine",
        severity="Moderate",
        specialist="Neurologist",
        symptom_pattern=["headache", "nausea", "vomiting", "blurred_vision", "dizziness",
                         "fatigue", "sensitivity_to_light", "sensitivity_to_sound"],
        description=(
            "Migraine is a neurological condition characterized by intense, debilitating headaches "
            "often accompanied by nausea, vomiting, and sensitivity to light and sound."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Rest in a dark, quiet room", priority=1),
            Precaution("Apply cold compress to forehead or temples", priority=2),
            Precaution("Take prescribed triptan or NSAID at onset of symptoms", priority=3),
            Precaution("Avoid bright lights, loud noises, and strong odours", priority=4),
            Precaution("Consult neurologist if migraines occur more than 4×/month", priority=5),
        ],
    ),

    "COVID-19": DiseaseMetadata(
        name="COVID-19",
        severity="Moderate",
        specialist="Pulmonologist",
        symptom_pattern=["fever", "cough", "fatigue", "loss_of_taste", "loss_of_smell",
                         "headache", "sore_throat", "shortness_of_breath", "body_ache"],
        description=(
            "COVID-19 is a respiratory illness caused by the SARS-CoV-2 virus. "
            "Most cases are mild to moderate, but severe complications can occur."
        ),
        emergency_risk=True,
        escalation_severity="Severe",
        escalation_threshold=85.0,
        precautions=[
            Precaution("Isolate immediately to prevent spread to others", priority=1),
            Precaution("Monitor oxygen levels — seek help if below 94%", priority=2),
            Precaution("Stay hydrated and rest; use antipyretics for fever", priority=3),
            Precaution("Track symptom progression daily", priority=4),
            Precaution("Seek emergency care for chest pain, confusion, or bluish lips", priority=5),
        ],
    ),

    "Typhoid": DiseaseMetadata(
        name="Typhoid",
        severity="Moderate",
        specialist="Infectious Disease Specialist",
        symptom_pattern=["high_fever", "headache", "nausea", "vomiting", "stomach_pain",
                         "fatigue", "toxic_look_typhos"],
        description=(
            "Typhoid fever is a bacterial infection caused by Salmonella Typhi. "
            "It spreads through contaminated food and water and requires antibiotic treatment."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Complete the full prescribed antibiotic course", priority=1),
            Precaution("Drink boiled or purified water only", priority=2),
            Precaution("Eat only freshly prepared, thoroughly cooked food", priority=3),
            Precaution("Rest and stay hydrated", priority=4),
            Precaution("Seek medical care if fever is very high or confusion develops", priority=5),
        ],
    ),

    "Chicken Pox": DiseaseMetadata(
        name="Chicken Pox",
        severity="Moderate",
        specialist="General Physician",
        symptom_pattern=["itching", "skin_rash", "fatigue", "lethargy", "vomiting",
                         "loss_of_appetite", "mild_fever", "headache"],
        description=(
            "Chickenpox is a highly contagious viral infection causing an itchy, blister-like rash. "
            "It is usually mild in children but can be serious in adults and immunocompromised individuals."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Apply calamine lotion to reduce itching", priority=1),
            Precaution("Trim fingernails and avoid scratching to prevent scarring", priority=2),
            Precaution("Take prescribed antivirals if started within 24 h of rash", priority=3),
            Precaution("Isolate until all blisters have crusted over", priority=4),
            Precaution("Seek medical care if fever is very high or rash spreads to eyes", priority=5),
        ],
    ),

    "Psoriasis": DiseaseMetadata(
        name="Psoriasis",
        severity="Moderate",
        specialist="Dermatologist",
        symptom_pattern=["skin_rash", "joint_pain", "skin_peeling", "silver_like_dusting",
                         "small_dents_in_nails", "inflammatory_nails"],
        description=(
            "Psoriasis is a chronic autoimmune condition causing rapid buildup of skin cells "
            "that results in red, scaly patches."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Apply prescribed topical corticosteroids or vitamin D analogues", priority=1),
            Precaution("Moisturise regularly to prevent skin drying", priority=2),
            Precaution("Avoid triggers such as stress, infections, and certain medications", priority=3),
            Precaution("Use medicated shampoo for scalp psoriasis", priority=4),
            Precaution("Consult dermatologist for phototherapy or biologic therapy if severe", priority=5),
        ],
    ),

    "Arthritis": DiseaseMetadata(
        name="Arthritis",
        severity="Moderate",
        specialist="Rheumatologist",
        symptom_pattern=["joint_pain", "swelling_joints", "knee_pain", "hip_joint_pain",
                         "painful_walking", "fatigue", "movement_stiffness"],
        description=(
            "Arthritis is inflammation of one or more joints, causing pain and stiffness "
            "that typically worsens with age."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Take prescribed NSAIDs or DMARDs as directed", priority=1),
            Precaution("Engage in low-impact exercise such as swimming or cycling", priority=2),
            Precaution("Apply heat for stiffness and cold packs for acute pain", priority=3),
            Precaution("Maintain a healthy body weight to reduce joint stress", priority=4),
            Precaution("Consult rheumatologist for disease-modifying therapy if needed", priority=5),
        ],
    ),

    "Hypertension": DiseaseMetadata(
        name="Hypertension",
        severity="Moderate",
        specialist="Cardiologist",
        symptom_pattern=["headache", "chest_pain", "dizziness", "blurred_vision", "fatigue"],
        description=(
            "Hypertension (high blood pressure) is a long-term condition in which the force "
            "of blood against artery walls is consistently too high."
        ),
        emergency_risk=False,
        escalation_severity="Severe",
        escalation_threshold=90.0,
        precautions=[
            Precaution("Take prescribed antihypertensive medication regularly", priority=1),
            Precaution("Follow a low-sodium diet (DASH diet)", priority=2),
            Precaution("Exercise regularly — 30 minutes of moderate activity most days", priority=3),
            Precaution("Monitor blood pressure daily at home", priority=4),
            Precaution("Seek emergency care for very severe headache or chest pain", priority=5),
        ],
    ),

    "GERD": DiseaseMetadata(
        name="GERD",
        severity="Moderate",
        specialist="Gastroenterologist",
        symptom_pattern=["acidity", "indigestion", "chest_pain", "vomiting", "cough", "stomach_pain"],
        description=(
            "Gastroesophageal reflux disease (GERD) occurs when stomach acid repeatedly "
            "flows back into the oesophagus, irritating its lining."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Avoid trigger foods (spicy, fatty, acidic foods, caffeine, alcohol)", priority=1),
            Precaution("Eat smaller, more frequent meals; do not lie down for 2–3 h after eating", priority=2),
            Precaution("Elevate the head of your bed by 6–8 inches", priority=3),
            Precaution("Take prescribed proton pump inhibitors (PPIs) as directed", priority=4),
            Precaution("Seek medical care if symptoms worsen or swallowing becomes difficult", priority=5),
        ],
    ),

    "Peptic Ulcer Disease": DiseaseMetadata(
        name="Peptic Ulcer Disease",
        severity="Moderate",
        specialist="Gastroenterologist",
        symptom_pattern=["vomiting", "indigestion", "loss_of_appetite", "abdominal_pain",
                         "passage_of_gases", "internal_itching"],
        description=(
            "Peptic ulcer disease involves open sores in the lining of the stomach, "
            "small intestine, or oesophagus, usually caused by H. pylori or NSAIDs."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Take prescribed antibiotics (for H. pylori) and PPIs as directed", priority=1),
            Precaution("Avoid NSAIDs (ibuprofen, aspirin) — use paracetamol instead", priority=2),
            Precaution("Avoid alcohol, spicy food, and acidic beverages", priority=3),
            Precaution("Eat smaller meals and avoid skipping meals", priority=4),
            Precaution("Seek urgent care for severe abdominal pain or black tarry stools", priority=5),
        ],
    ),

    "Cervical Spondylosis": DiseaseMetadata(
        name="Cervical Spondylosis",
        severity="Moderate",
        specialist="Neurologist",
        symptom_pattern=["back_pain", "weakness_in_limbs", "neck_pain", "dizziness",
                         "movement_stiffness", "loss_of_balance"],
        description=(
            "Cervical spondylosis is age-related wear and tear of the cartilage and bones "
            "in the cervical (neck) spine, causing stiffness and sometimes nerve compression."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Use prescribed NSAIDs or muscle relaxants for pain relief", priority=1),
            Precaution("Do prescribed physiotherapy neck exercises regularly", priority=2),
            Precaution("Use a supportive pillow and maintain good posture", priority=3),
            Precaution("Apply heat or ice pack to the neck for symptom relief", priority=4),
            Precaution("Seek urgent care for progressive weakness or loss of bladder control", priority=5),
        ],
    ),

    "Diabetes": DiseaseMetadata(
        name="Diabetes",
        severity="Moderate",
        specialist="Endocrinologist",
        symptom_pattern=["fatigue", "weight_loss", "polyuria", "irregular_sugar_level",
                         "excessive_hunger", "blurred_vision"],
        description=(
            "Diabetes is a metabolic disease that causes high blood sugar. "
            "Type 2 diabetes is the most common form and is largely lifestyle-related."
        ),
        emergency_risk=False,
        escalation_severity="Severe",
        escalation_threshold=88.0,
        precautions=[
            Precaution("Monitor blood glucose levels regularly as advised", priority=1),
            Precaution("Take prescribed insulin or oral medications consistently", priority=2),
            Precaution("Follow a low-glycaemic diet and avoid sugary foods", priority=3),
            Precaution("Exercise regularly — improves insulin sensitivity", priority=4),
            Precaution("Seek immediate care for very high/low blood sugar (DKA / hypoglycaemia)", priority=5),
        ],
    ),

    "Varicose Veins": DiseaseMetadata(
        name="Varicose Veins",
        severity="Moderate",
        specialist="Vascular Surgeon",
        symptom_pattern=["varicose_veins", "fatigue", "cramps", "swollen_legs",
                         "prominent_veins_on_calf", "swollen_blood_vessels", "painful_walking"],
        description=(
            "Varicose veins are twisted, enlarged veins, most often in the legs. "
            "They are caused by weak or damaged vein valves."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Wear prescribed compression stockings during the day", priority=1),
            Precaution("Elevate legs above heart level when resting", priority=2),
            Precaution("Exercise regularly — walking improves circulation", priority=3),
            Precaution("Avoid standing or sitting for prolonged periods", priority=4),
            Precaution("Consult vascular surgeon if pain, ulcers, or bleeding develop", priority=5),
        ],
    ),

    # ------------------------------------------------------------------ #
    #  SEVERE DISEASES                                                     #
    # ------------------------------------------------------------------ #

    "Bronchial Asthma": DiseaseMetadata(
        name="Bronchial Asthma",
        severity="Severe",
        specialist="Pulmonologist",
        symptom_pattern=["cough", "fatigue", "chest_pain", "breathlessness", "phlegm",
                         "mucoid_sputum"],
        description=(
            "Bronchial asthma is a chronic inflammatory disease of the airways causing "
            "recurrent episodes of wheezing, breathlessness, and chest tightness."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Use prescribed rescue inhaler (albuterol) at first sign of attack", priority=1),
            Precaution("Take daily controller medication (ICS) as prescribed", priority=2),
            Precaution("Avoid known triggers — dust, pollen, smoke, pet dander", priority=3),
            Precaution("Monitor peak flow readings regularly", priority=4),
            Precaution("Call emergency services if inhaler gives no relief within 15 min", priority=5),
        ],
    ),

    "Pneumonia": DiseaseMetadata(
        name="Pneumonia",
        severity="Severe",
        specialist="Pulmonologist",
        symptom_pattern=["fever", "cough", "fatigue", "shortness_of_breath", "chest_pain",
                         "chills", "sweating", "body_ache"],
        description=(
            "Pneumonia is an infection that inflames the air sacs in one or both lungs. "
            "It can range from mild to life-threatening and requires prompt medical attention."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Seek immediate medical attention — pneumonia requires urgent care", priority=1),
            Precaution("Complete prescribed antibiotic course even if symptoms improve", priority=2),
            Precaution("Rest and avoid all physical exertion", priority=3),
            Precaution("Monitor oxygen levels with pulse oximeter if available", priority=4),
            Precaution("Return to ER if breathing worsens or chest pain increases", priority=5),
        ],
    ),

    "Malaria": DiseaseMetadata(
        name="Malaria",
        severity="Severe",
        specialist="Infectious Disease Specialist",
        symptom_pattern=["fever", "chills", "sweating", "headache", "body_ache",
                         "fatigue", "nausea", "vomiting"],
        description=(
            "Malaria is a life-threatening disease caused by Plasmodium parasites "
            "transmitted by infected mosquitoes. Early treatment is critical."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Seek immediate medical treatment — malaria can progress rapidly", priority=1),
            Precaution("Complete full course of antimalarial medication", priority=2),
            Precaution("Use insecticide-treated mosquito nets while sleeping", priority=3),
            Precaution("Apply EPA-registered mosquito repellent outdoors", priority=4),
            Precaution("Monitor for recurrence of fever", priority=5),
        ],
    ),

    "Dengue": DiseaseMetadata(
        name="Dengue",
        severity="Severe",
        specialist="Infectious Disease Specialist",
        symptom_pattern=["fever", "headache", "body_ache", "joint_pain", "rash",
                         "nausea", "vomiting", "fatigue"],
        description=(
            "Dengue is a mosquito-borne viral infection causing flu-like symptoms. "
            "Severe dengue can be life-threatening and requires medical monitoring."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Seek medical care immediately for proper monitoring", priority=1),
            Precaution("Stay hydrated with oral fluids; IV fluids may be needed", priority=2),
            Precaution("Monitor platelet counts and watch for bleeding signs", priority=3),
            Precaution("Avoid NSAIDs — use paracetamol only for fever", priority=4),
            Precaution("Go to ER immediately for severe abdominal pain or bleeding", priority=5),
        ],
    ),

    "Jaundice": DiseaseMetadata(
        name="Jaundice",
        severity="Severe",
        specialist="Hepatologist",
        symptom_pattern=["itching", "vomiting", "fatigue", "weight_loss", "high_fever",
                         "dark_urine", "yellowing_of_eyes", "abdominal_pain"],
        description=(
            "Jaundice is a yellowing of the skin and eyes caused by excess bilirubin. "
            "It signals an underlying liver, gallbladder, or blood disorder."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Seek immediate medical evaluation to determine the cause", priority=1),
            Precaution("Avoid alcohol completely", priority=2),
            Precaution("Follow a low-fat, high-carbohydrate diet as advised", priority=3),
            Precaution("Stay well hydrated with water and clear fluids", priority=4),
            Precaution("Do not take any medications without doctor's approval", priority=5),
        ],
    ),

    "Dimorphic Hemorrhoids": DiseaseMetadata(
        name="Dimorphic Hemorrhoids",
        severity="Moderate",
        specialist="Proctologist",
        symptom_pattern=["constipation", "pain_in_anal_region", "bloody_stool",
                         "irritation_in_anus", "pain_during_bowel_movements"],
        description=(
            "Haemorrhoids (piles) are swollen veins in the rectum or anus. "
            "Dimorphic haemorrhoids present as both internal and external types simultaneously."
        ),
        emergency_risk=False,
        precautions=[
            Precaution("Increase dietary fibre to soften stools", priority=1),
            Precaution("Stay well hydrated to avoid straining", priority=2),
            Precaution("Use sitz baths (warm water soaks) for pain relief", priority=3),
            Precaution("Apply OTC haemorrhoid cream or suppositories", priority=4),
            Precaution("Consult a proctologist if bleeding is heavy or persistent", priority=5),
        ],
    ),

    # ------------------------------------------------------------------ #
    #  EMERGENCY-ONLY AUGMENTED DISEASES                                   #
    # ------------------------------------------------------------------ #

    "Heart Attack": DiseaseMetadata(
        name="Heart Attack",
        severity="Severe",
        specialist="Cardiologist",
        symptom_pattern=["chest_pain", "shortness_of_breath", "nausea", "sweating",
                         "dizziness", "fatigue", "arm_pain", "jaw_pain"],
        description=(
            "A heart attack (myocardial infarction) occurs when blood flow to the heart "
            "is severely reduced or blocked. It is a life-threatening medical emergency."
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
        symptom_pattern=["confusion", "blurred_vision", "headache", "dizziness",
                         "muscle_weakness", "fatigue", "facial_drooping", "speech_difficulty"],
        description=(
            "A stroke occurs when blood supply to part of the brain is interrupted or reduced. "
            "Time-critical emergency — early treatment significantly improves outcomes."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Call emergency services (108/911) immediately", priority=1),
            Precaution("Note the exact time symptoms first appeared", priority=2),
            Precaution("Keep patient calm and lying flat on their side if unconscious", priority=3),
            Precaution("Do not give any food, water, or medication by mouth", priority=4),
            Precaution("Treatment within 4.5 hours significantly improves outcomes", priority=5),
        ],
    ),

    "Severe Respiratory Distress": DiseaseMetadata(
        name="Severe Respiratory Distress",
        severity="Severe",
        specialist="Pulmonologist",
        symptom_pattern=["shortness_of_breath", "chest_pain", "cough", "confusion",
                         "fatigue", "fever"],
        description=(
            "Severe respiratory distress is a life-threatening condition where the lungs "
            "cannot provide enough oxygen to the body. Immediate emergency care is required."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Call emergency services (108/911) immediately", priority=1),
            Precaution("Sit upright and lean slightly forward to optimise breathing", priority=2),
            Precaution("Do not lie flat — this worsens respiratory effort", priority=3),
            Precaution("Use prescribed rescue inhaler if available", priority=4),
            Precaution("Loosen tight clothing around neck and chest", priority=5),
        ],
    ),

    "Epilepsy": DiseaseMetadata(
        name="Epilepsy",
        severity="Severe",
        specialist="Neurologist",
        symptom_pattern=["seizure", "confusion", "fatigue", "headache", "muscle_weakness", "dizziness"],
        description=(
            "Epilepsy is a neurological disorder characterised by recurrent seizures. "
            "Seizures vary in intensity; prolonged episodes require emergency care."
        ),
        emergency_risk=True,
        precautions=[
            Precaution("Ensure airway is clear; gently turn person onto their side", priority=1),
            Precaution("Do not restrain the person or put anything in their mouth", priority=2),
            Precaution("Time the seizure — call emergency services if more than 5 minutes", priority=3),
            Precaution("Remove nearby sharp objects to prevent injury", priority=4),
            Precaution("Stay with the person until fully conscious and oriented", priority=5),
        ],
    ),
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

SEVERITY_ORDER: dict[str, int] = {"Mild": 1, "Moderate": 2, "Severe": 3}


def get_disease(name: str) -> DiseaseMetadata | None:
    return DISEASE_REGISTRY.get(name)


def get_severity(name: str) -> str:
    disease = DISEASE_REGISTRY.get(name)
    return disease.severity if disease else "Moderate"


def get_specialist(name: str) -> str:
    disease = DISEASE_REGISTRY.get(name)
    return disease.specialist if disease else "General Physician"


def get_precautions(name: str) -> list[Precaution]:
    disease = DISEASE_REGISTRY.get(name)
    return disease.precautions if disease else []


def is_emergency_risk(name: str) -> bool:
    disease = DISEASE_REGISTRY.get(name)
    return disease.emergency_risk if disease else False


def get_escalation(name: str) -> tuple[str | None, float | None]:
    disease = DISEASE_REGISTRY.get(name)
    if disease is None:
        return None, None
    return disease.escalation_severity, disease.escalation_threshold


FALLBACK_PRECAUTIONS_BY_SEVERITY: dict[str, list[Precaution]] = {
    "Mild": [
        Precaution("Rest and monitor your symptoms", priority=1),
        Precaution("Stay hydrated and maintain a balanced diet", priority=2),
        Precaution("Use OTC remedies as appropriate", priority=3),
        Precaution("Consult a healthcare professional if symptoms worsen", priority=4),
    ],
    "Moderate": [
        Precaution("Schedule an appointment with a healthcare provider", priority=1),
        Precaution("Monitor symptom progression closely", priority=2),
        Precaution("Avoid strenuous activity until evaluated", priority=3),
        Precaution("Seek immediate care if symptoms suddenly worsen", priority=4),
    ],
    "Severe": [
        Precaution("Seek immediate medical attention — urgent evaluation needed", priority=1),
        Precaution("Visit the nearest emergency department without delay", priority=2),
        Precaution("Arrange transportation — do not drive yourself", priority=3),
        Precaution("Have a caregiver accompany you if possible", priority=4),
    ],
}
