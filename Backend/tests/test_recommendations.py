from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register_and_login(email: str, username: str, password: str = "pass123") -> dict:
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_recommendation_endpoints_return_lists():
    headers = _register_and_login("recuser@example.com", "recuser")

    for path in ["/api/v1/recommendations/users", "/api/v1/recommendations/posts", "/api/v1/recommendations/trending"]:
        resp = client.get(path, headers=headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


def test_follow_then_recommend():
    """Basic smoke test: follow a user, hit recommendations."""
    h_alice = _register_and_login("alice@example.com", "alice")
    h_bob = _register_and_login("bob@example.com", "bob")

    # Alice follows bob
    client.post("/api/v1/follows/bob", headers=h_alice)

    # Bob's recommendations should work
    resp = client.get("/api/v1/recommendations/users", headers=h_bob)
    assert resp.status_code == 200
