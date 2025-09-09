# tests/test_medicines.py
from fastapi.testclient import TestClient


def create_admin_token(client: TestClient, username="muser", password="pwd"):
    client.post("/users/create", json={"username": username, "password": password, "role": "admin"})
    r = client.post("/users/token", data={"username": username, "password": password})
    return r.json()["access_token"]


def test_add_and_search_medicine(client: TestClient):
    t = create_admin_token(client)
    headers = {"Authorization": f"Bearer {t}"}
    payload = {"name": "Paracetamol", "manufacturer": "Pharma", "quantity": 20}
    r = client.post("/medicines", json=payload, headers=headers)
    assert r.status_code == 201
    mid = r.json()["id"]

    r2 = client.get("/medicines?q=Paracet&page=1", headers=headers)
    assert r2.status_code == 200
    assert any(int(m["id"]) == mid for m in r2.json())


def test_adjust_stock(client: TestClient):
    t = create_admin_token(client, username="muser2", password="pwd2")
    headers = {"Authorization": f"Bearer {t}"}
    payload = {"name": "Ibuprofen", "quantity": 2}
    r = client.post("/medicines", json=payload, headers=headers)
    assert r.status_code == 201
    mid = r.json()["id"]

    r2 = client.patch(f"/medicines/{mid}/adjust?delta=5", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["quantity"] == 7
