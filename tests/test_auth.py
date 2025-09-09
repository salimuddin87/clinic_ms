# tests/test_auth.py
def test_create_user_and_get_token(client):
    # create a user
    payload = {"username": "testuser", "full_name": "Test User", "role": "doctor", "password": "secret"}
    r = client.post("/users/create", json=payload)
    assert r.status_code == 201

    # login to get token
    r2 = client.post("/users/token", data={"username": "testuser", "password": "secret"})
    assert r2.status_code == 200
    data = r2.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
