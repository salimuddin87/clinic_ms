# tests/test_appointments.py
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


def create_doctor_token(client: TestClient, username="doc1", password="pwd"):
    client.post("/users/create", json={"username": username, "password": password, "role": "doctor"})
    r = client.post("/users/token", data={"username": username, "password": password})
    return r.json()["access_token"]


def test_create_and_cancel_appointment(client: TestClient):
    token = create_doctor_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    # create patient
    p = client.post("/patients", json={"first_name": "ApptTest"}, headers=headers)
    assert p.status_code == 201
    pid = p.json()["id"]

    scheduled = (datetime.utcnow() + timedelta(days=1)).isoformat()
    ap_payload = {"patient_id": pid, "scheduled_at": scheduled, "reason": "Checkup"}
    r = client.post("/appointments", json=ap_payload, headers=headers)
    assert r.status_code == 201
    apid = r.json()["id"]

    r2 = client.patch(f"/appointments/{apid}/cancel", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "canceled"
