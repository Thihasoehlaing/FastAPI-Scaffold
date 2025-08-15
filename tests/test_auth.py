def test_register_login_me_flow(client):
    # register
    payload = {"email": "alice@example.com", "name": "Alice", "password": "secret123"}
    r = client.post("/v1/auth/register", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"]["email"] == payload["email"]

    # login
    r = client.post("/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r.status_code == 200
    token = r.json()["data"]["access_token"]
    assert token

    # me
    r = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    me = r.json()["data"]
    assert me["email"] == payload["email"]
