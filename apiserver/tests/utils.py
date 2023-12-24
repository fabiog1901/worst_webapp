from fastapi.testclient import TestClient
from apiserver.main import app
import apiserver.db as db
import apiserver.dependencies as dep
import pytest
import httpx
import random
from uuid import UUID

from apiserver.models import UserInDB

client = TestClient(app)


# PYTEST FIXTURES
@pytest.fixture
def login(username: str = "dummyadmin", password: str = "dummyadmin") -> str:
    r = client.post("/login", data={"username": username, "password": password})

    assert r.status_code == 200

    return r.json()["access_token"]


@pytest.fixture(scope="session")
def setup_test():
    db.load_schema("storage/worst.ddl.sql")

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


def s3_upload(presigned_put_url: str, filename: str):
    try:
        with open(filename, "rb") as f:
            txt = f.read()

        r = httpx.put(presigned_put_url, data=txt)  # type: ignore

        assert r.status_code == 200

    except FileNotFoundError:
        print(f"Couldn't find {filename}.")


def s3_download(presigned_get_url: str, filename: str):
    try:
        with open(filename, "wb") as f:
            with httpx.stream("GET", presigned_get_url) as r:
                assert r.status_code == 200

                for data in r.iter_bytes():
                    f.write(data)

    except FileNotFoundError:
        print(f"Couldn't find {filename}.")
