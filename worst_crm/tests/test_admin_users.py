from fastapi.testclient import TestClient

from worst_crm.main import app

client = TestClient(app)


# create 3 dummy users
# def test_prepare_dummy_users():
#     db.create_user(
#         UserInDB(
#             user_id='dummyadmin',
#             is_disabled=False,
#             scopes = ['rw', 'admin'],
#             hashed_password=dep.get_password_hash('dummyadmin')
#         )
#     )

#     db.create_user(
#         UserInDB(
#             user_id='dummyrw',
#             is_disabled=False,
#             scopes = ['rw'],
#             hashed_password=dep.get_password_hash('dummyrw')
#         )
#     )

#     db.create_user(
#         UserInDB(
#             user_id='dummyro',
#             is_disabled=False,
#             scopes = [],
#             hashed_password=dep.get_password_hash('dummyro')
#         )
#     )


# GENERAL
def test_healthcheck():
    r = client.get("/healthcheck")
    assert r.status_code == 200
    assert r.json() == {}


def login(username: str = "admin", password: str = "worstcrm") -> str:
    r = client.post("/login", data={"username": username, "password": password})

    return r.json()["access_token"]


def test_login(username: str = "admin", password: str = "worstcrm"):
    token = login()

    assert token is not None


def ztest_user_locked(username: str = "ro", password: str = "xxxxxxxxxx"):
    r = client.post("/login", data={"username": username, "password": password})
    assert r.status_code == 401

    r = client.post("/login", data={"username": username, "password": password})
    assert r.status_code == 401

    r = client.post("/login", data={"username": username, "password": password})
    assert r.status_code == 401

    r = client.post("/login", data={"username": username, "password": password})
    assert r.status_code == 406
