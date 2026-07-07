# Machine Learning Module

Trained models and training pipeline for SymptomScope AI.

## Models

| Model | Algorithm | Purpose |
|-------|-----------|---------|
| `decision_tree_v1.pkl` | DecisionTreeClassifier (max_depth=10) | Fast interpretable predictions |
| `random_forest_v1.pkl` | RandomForestClassifier (150 estimators, max_depth=12) | Higher accuracy ensemble |
| `label_encoder_v1.pkl` | LabelEncoder | Disease name encoding |
| `symptom_columns_v1.pkl` | list[str] | 31 symptom feature names |

## Training Pipeline

`ml/training/train_models.py`:
- Generates ~3,100 synthetic samples (150-300 per disease class)
- Uses noise-injected symptom patterns
- Trains both Decision Tree and Random Forest
- Serializes models via `joblib`

## Supported Diseases

15 diseases with 31 binary symptom features.

## Important

Models are trained on **synthetic data** only. They must not be used for real clinical diagnosis without proper validation on real patient data.
