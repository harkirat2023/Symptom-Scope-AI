import asyncio
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://symptomscope.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TestRequest(BaseModel):
    prediction_id: str

@app.post("/api/v1/recovery-plan/generate")
async def test_generate(request: TestRequest):
    return {
        "id": "test-id",
        "user_id": "test-user",
        "prediction_id": request.prediction_id,
        "disease": "Test Disease",
        "confidence": 95,
        "severity": "moderate",
        "symptoms": ["fever", "cough"],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "recovery_timeline": ["Week 1: Rest", "Week 2: Recovery"],
        "diet_recommendations": {},
        "foods_to_eat": ["Water"],
        "foods_to_avoid": [],
        "hydration_advice": "Drink water",
        "sleep_recommendation": "Sleep well",
        "exercise_recommendation": "Walk",
        "daily_physical_activity": ["Walking"],
        "lifestyle_changes": ["Quit smoking"],
        "medicines_disclaimer": "Consult doctor",
        "when_to_visit_doctor": ["If worsens"],
        "emergency_warning_signs": ["Emergency signs"],
        "mental_wellness_tips": ["Relax"],
        "recovery_checklist": ["Take medicine"],
        "progress_tracker": {"week_1": "Goals"},
        "version": 1
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
