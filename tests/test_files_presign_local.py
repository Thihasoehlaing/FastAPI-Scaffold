def test_presign_not_supported_on_local(client):
    payload = {"filename": "pic.png", "content_type": "image/png", "is_public": True}
    r = client.post("/v1/files/presign", json=payload)
    assert r.status_code == 200  # controller returns envelope with error
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_SUPPORTED"
