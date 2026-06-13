from fastapi.testclient import TestClient
from main import app
import requests

API_ENDPOINT = 'http://127.0.0.1:8000/api/v1'

client = TestClient(app)

# ======= System Tests =========
def test_health():
    response = client.get(f'{API_ENDPOINT}/health')
    assert response.status_code == 200




# ======= Functional Tests =========

# Verify that client with tax id "95-1234567" exist 
r = requests.get(API_ENDPOINT + "/clients", {"tax_id":"95-1234567"})
assert r.status_code == 200


# Verify that a "note" will NOT be created without providing client id
test_note = {
  # "client_id": "cli_99011",
  "note_content": "Test Note." 
}
r = requests.post(API_ENDPOINT + "/clients/notes", json=test_note)
assert r.status_code == 422


print("Test complete.")