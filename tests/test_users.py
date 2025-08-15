def test_users_list_starts_empty(client):
    r = client.get("/v1/users")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["pagination"]["total"] == 0

def test_users_created_via_register_appear_in_list(client):
    # Register two users
    for i in range(2):
        client.post("/v1/auth/register", json={
            "email": f"user{i}@example.com",
            "name": f"User {i}",
            "password": "password123"
        })

    r = client.get("/v1/users?limit=10&page=1")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["pagination"]["total"] >= 2
    emails = {u["email"] for u in body["data"]}
    assert "user0@example.com" in emails
    assert "user1@example.com" in emails
