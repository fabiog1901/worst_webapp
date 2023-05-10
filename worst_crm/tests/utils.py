from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import UserInDB, Account
import worst_crm.db as db
import worst_crm.dependencies as dep
import pytest
import minio
import os
import httpx


S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_USE_SECURE_TLS = (
    True
    if os.getenv("S3_USE_SECURE_TLS", "True").lower()
    in ["true", "1", "t", "y", "yes", "on"]
    else False
)
S3_BUCKET = os.getenv("S3_BUCKET")


client = TestClient(app)

minio_client = minio.Minio(
    endpoint=S3_ENDPOINT_URL,
    secure=S3_USE_SECURE_TLS,
    access_key=S3_ACCESS_KEY,
    secret_key=S3_SECRET_KEY,
)


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


def s3_upload(filename: str = "ss.png", s3_object_name: str | None = "gino"):
    r = client.get(f"/presigned-put-url?name={s3_object_name}")
    url = r.text

    try:
        with open(filename, "rb") as f:
            txt = f.read()

        # r = requests.put(url, files={'file': open(filename, 'rb')})
        r = httpx.put(url, data=txt)  # type: ignore

        assert r.status_code == 200

    except FileNotFoundError:
        print(f"Couldn't find {filename}.")


def s3_download(filename: str = "ss1.png", s3_object_name: str | None = "gino"):
    r = client.get(f"/presigned-get-url?name={s3_object_name}")
    url = r.text

    try:
        with open(filename, "wb") as f:
            with httpx.stream("GET", url) as r:
                assert r.status_code == 200

                for data in r.iter_bytes():
                    f.write(data)

    except FileNotFoundError:
        print(f"Couldn't find {filename}.")


def test_create_account_x(login, setup_test):
    token = login

    r = client.post(
        "/accounts",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_acc1",
            "owned_by": "dummyadmin",
            "text": "dummy descr",
            "status": "NEW",
            "tags": ["t11", "t22", "t22"]
        }""",
    )

    assert r.status_code == 200

    acc = Account(**r.json())

    att_name = str(acc.account_id) + "/" + "ss.png"
    s3_upload("ss.png", att_name)

    # UPDATE
    r = client.put(
        f"/accounts/{acc.account_id}",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_acc1",
            "description": "dummy descr UPDATED",
            "status": "NEW",
            "attachments": ['ss.png'],
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t5555"],
            "data": {"k": "v", "kk": "vv"}
        }""",
    )

    upd_acc = Account(**r.json())
