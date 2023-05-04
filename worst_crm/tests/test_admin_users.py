from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import UserInDB
import worst_crm.db as db
import worst_crm.dependencies as dep

client = TestClient(app)

def test_setup():
    db.delete_user('dummyadmin')

    assert db.create_user(
        UserInDB(
            user_id='dummyadmin',
            is_disabled=False,
            scopes = ['rw', 'admin'],
            hashed_password=dep.get_password_hash('dummyadmin')
        )
    )

def login(username: str = "dummyadmin", password: str = "dummyadmin") -> str | None:
    r = client.post("/login", data={"username": username, "password": password})

    if r.status_code == 401:
        return None
    
    return r.json()["access_token"]


# GENERAL
def test_healthcheck():
    r = client.get("/healthcheck")
    assert r.status_code == 200
    assert r.json() == {}


def test_login(username: str = "admin", password: str = "worstcrm"):
    token = login()

    assert token is not None


def test_user_locked():
    
    for _ in range(3):
        r = client.post("/login", data={"username": 'dummyadmin', "password": 'wrong-password'})
        assert r.status_code == 401

    r = client.post("/login", data={"username": 'dummyadmin', "password": 'wrong-password'})
    assert r.status_code == 406


def test_cleanup():
    assert db.delete_user('dummyadmin')
