import sys
import os
os.chdir(r"D:\1. PLACEMENT\1A. PROJECTS\Symptom Scope AI")
sys.path.insert(0, "backend")

from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test with invalid ID - should return 400 now
response = client.post("/api/v1/recovery-plan/generate", json={"prediction_id": "test123"})
print(f"Invalid ID test - Status: {response.status_code}")
print(f"Response: {response.text}")

# Test with valid format ObjectId but non-existent - should return 404
from bson.objectid import ObjectId
valid_id = str(ObjectId())
response = client.post("/api/v1/recovery-plan/generate", json={"prediction_id": valid_id})
print(f"\nValid format, non-existent - Status: {response.status_code}")
print(f"Response: {response.text}")

# Test health
health = client.get("/health")
print(f"\nHealth: {health.json()}")
