from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_healthcheck():
    r = client.get("/healthcheck")
    assert r.status_code == 200
    assert r.json() == {}


def test_login(username: str = "admin", password: str = "secret"):
    r = client.post("/login", data={"username": username, "password": password})

    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token is not None
    return token


def test_get_accounts():
    token = test_login()
    r = client.get("/accounts", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

    assert len(r.content) > 0


def test_get_accounts_non_auth():
    # token = test_login()
    r = client.get("/accounts")  # , headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_create_accounts():
    token = test_login()
    r = client.get("/accounts", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

    assert len(r.content) > 0
