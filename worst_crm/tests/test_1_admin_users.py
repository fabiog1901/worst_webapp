from fastapi.testclient import TestClient
from worst_crm.main import app
import worst_crm.tests.utils as utils

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
