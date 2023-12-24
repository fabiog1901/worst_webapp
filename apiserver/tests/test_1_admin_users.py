from fastapi.testclient import TestClient
from apiserver.main import app
import apiserver.tests.utils as utils

client = TestClient(app)


def ztest_user_locked():
    for _ in range(3):
        r = client.post(
            "/login", data={"username": "dummyadmin", "password": "wrong-password"}
        )
        assert r.status_code == 401

    r = client.post(
        "/login", data={"username": "dummyadmin", "password": "wrong-password"}
    )
    assert r.status_code == 406
