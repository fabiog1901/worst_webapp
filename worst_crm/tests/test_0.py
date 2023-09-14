from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.tests import utils
from worst_crm.tests.utils import login, setup_test

client = TestClient(app)


def test1(setup_test):
    r = client.get("/api")

    assert r.status_code == 200
