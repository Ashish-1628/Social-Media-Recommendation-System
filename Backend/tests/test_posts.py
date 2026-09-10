from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _auth_headers(email: str, username: str, password: str = "pass123") -> dict:
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_get_post():
    headers = _auth_headers("poster@example.com", "poster")
    create = client.post(
        "/api/v1/posts/",
        json={"content": "Hello GraphConnect!", "tags": []},
        headers=headers,
    )
    assert create.status_code == 201
    post_id = create.json()["id"]

    get = client.get(f"/api/v1/posts/{post_id}", headers=headers)
    assert get.status_code == 200
    assert get.json()["content"] == "Hello GraphConnect!"


def test_like_and_unlike():
    headers = _auth_headers("liker@example.com", "liker")
    post = client.post(
        "/api/v1/posts/",
        json={"content": "Like me!"},
        headers=headers,
    )
    post_id = post.json()["id"]

    like = client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
    assert like.status_code == 200

    # Double-like should fail
    double = client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
    assert double.status_code == 400

    unlike = client.delete(f"/api/v1/posts/{post_id}/like", headers=headers)
    assert unlike.status_code == 200
