# tests/test_patients.py
from fastapi.testclient import TestClient


def create_token(client: TestClient, username="puser", password="pwd", role="doctor"):
    # create user and obtain token
    client.post("/users/create", json={"username": username, "password": password, "role": role})
    r = client.post("/users/token", data={"username": username, "password": password})
    return r.json()["access_token"]


def test_create_and_get_patient(client: TestClient):
    token = create_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"first_name": "Asha", "last_name": "K", "phone": "999888777"}
    r = client.post("/patients", json=payload, headers=headers)
    assert r.status_code == 201
    data = r.json()
    assert data["first_name"] == "Asha"
    pid = data["id"]

    r2 = client.get(f"/patients/{pid}", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["id"] == pid


def test_list_patients_pagination(client: TestClient):
    token = create_token(client, username="puser2", password="pwd2")
    headers = {"Authorization": f"Bearer {token}"}

    # create 12 patients
    for i in range(12):
        client.post("/patients", json={"first_name": f"List{i}"}, headers=headers)

    r = client.get("/patients?page=1", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) <= 10
