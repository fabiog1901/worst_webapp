from fastapi.testclient import TestClient
from apiserver.main import app
from apiserver.tests import utils
from apiserver.tests.utils import login, setup_test

client = TestClient(app)


def test1(setup_test):
    r = client.get("/api")

    assert r.status_code == 200
