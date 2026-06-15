from fastapi.testclient import TestClient
from secureagent.main import app
import requests

API_ENDPOINT = 'http://127.0.0.1:8000/api/v1'

client = TestClient(app)

# ======= System Tests =========
def test_health():
    response = client.get(f'{API_ENDPOINT}/health')
    assert response.status_code == 200




# ======= Functional Tests =========

# Verify that client with tax id "95-1234567" exist 
def test_client_exists():
  response = client.get(f"{API_ENDPOINT}/clients/95-1234567")
  assert response.status_code == 200


# Verify that a "note" will NOT be created without providing client id
def test_note_creation():
  response = client.post(f"{API_ENDPOINT}/clients/notes", json={"note_content": "Test Note."})
  assert response.status_code == 422


print("Test complete.")