# Backend Services

Business logic layer for SymptomScope AI.

## Architecture

Each service encapsulates a single domain concern:

| Service | Responsibility |
|---------|---------------|
| `prediction_service.py` | ML ensemble inference (Decision Tree + Random Forest), confidence scoring, explainability |
| `feature_engineering.py` | Symptom one-hot encoding into 31-element feature vector |
| `severity_service.py` | Disease severity classification with escalation rules |
| `precaution_service.py` | Disease-to-precaution mapping with priority sorting |
| `emergency_service.py` | Emergency detection (severity/confidence/escalation triggers) |
| `doctor_service.py` | Doctor recommendation with composite scoring |
| `hospital_service.py` | Hospital search with disease-aware matching |
| `symptom_search_service.py` | Symptom search with category filtering |
| `search_service.py` | Relevance scoring and sorting utilities |
| `analytics_service.py` | Health analytics computation with caching |
| `report_service.py` | Report generation from prediction records |
| `report_export_service.py` | CSV and PDF export using reportlab |
| `disease_registry.py` | Centralized DiseaseMetadata dataclass for all 15 diseases |

## Usage

Services follow dependency injection via `Depends()`.

```python
@router.post("/predict")
async def predict(
    prediction_service: PredictionService = Depends(),
): ...
```
