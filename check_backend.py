import sys
sys.path.insert(0, '.')

from backend.api.v1.recovery import router
from fastapi.testclient import TestClient
from backend.api.v1.recovery import router as recovery_router

app = TestClient(recovery_router)

# Test the endpoint directly
response = app.post("/api/v1/recovery-plan/generate", json={"prediction_id": "test123"})
print("Status:", response.status_code)
print("Response:", response.text)
