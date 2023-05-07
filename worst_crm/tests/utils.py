from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import UserInDB
import worst_crm.db as db
import worst_crm.dependencies as dep
import pytest

client = TestClient(app)

@pytest.fixture
def login(username: str = "dummyadmin", password: str = "dummyadmin") -> str:
    r = client.post("/login", data={"username": username, "password": password})

    assert r.status_code == 200

    return r.json()["access_token"]

@pytest.fixture(scope="session")
def setup_test():
    db.load_schema("storage/worst_crm.ddl.sql")

    assert db.create_user(
        UserInDB(
            user_id="dummyadmin",
            is_disabled=False,
            scopes=["rw", "admin"],
            hashed_password=dep.get_password_hash("dummyadmin"),
        )
    )


# GENERAL
def test_healthcheck():
    r = client.get("/healthcheck")
    assert r.status_code == 200
    assert r.json() == {}
