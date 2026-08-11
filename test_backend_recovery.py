import sys
import os
os.chdir(r"D:\1. PLACEMENT\1A. PROJECTS\Symptom Scope AI")
sys.path.insert(0, "backend")

# Test the actual recovery endpoint
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test without auth first (will use dev-mode fallback)
response = client.post("/api/v1/recovery-plan/generate", json={"prediction_id": "test123"})
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
if response.status_code != 200:
    # Check if it's an auth issue
    print(f"Headers: {dict(response.headers)}")

# Also test health
health = client.get("/health")
print(f"Health: {health.json()}")
