import sys
sys.path.insert(0, '.')

# Set PYTHONPATH properly
import os
os.environ['PYTHONPATH'] = os.getcwd() + ':' + os.environ.get('PYTHONPATH', '')

from backend.api.v1.recovery import router
from fastapi.testclient import TestClient

client = TestClient(router)
response = client.post("/api/v1/recovery-plan/generate", json={"prediction_id": "test123"})
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")
if response.status_code != 200:
    print(f"Headers: {dict(response.headers)}")
