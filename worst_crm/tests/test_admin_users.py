from fastapi.testclient import TestClient
from worst_crm.main import app
import worst_crm.tests.test_utils as utils

client = TestClient(app)


def test_user_locked():
    utils.test_setup()

    for _ in range(3):
        r = client.post(
            "/login", data={"username": "dummyadmin", "password": "wrong-password"}
        )
        assert r.status_code == 401

    r = client.post(
        "/login", data={"username": "dummyadmin", "password": "wrong-password"}
    )
    assert r.status_code == 406

    utils.test_cleanup()
