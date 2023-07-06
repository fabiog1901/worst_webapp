import random
from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import (
    Artifact,
    ArtifactOverview,
    ArtifactOverviewWithAccountName,
    ArtifactOverviewWithOpportunityName,
)
from worst_crm.tests import utils
from worst_crm.tests.utils import login
import hashlib
import validators
from faker import Faker

fake = Faker()

client = TestClient(app)


ACCOUNT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
OPPORTUNITY_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
ARTIFACT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
ARTIFACT_SCHEMA_ID = "ART-SCHEMA-1"


def test_get_artifacts_non_auth():
    r = client.get("/artifacts")

    assert r.status_code == 401


def test_create_artifact(login):
    r = client.post(
        "/artifacts",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "ART-1",
            "account_id": ACCOUNT_ID,
            "opportunity_id": OPPORTUNITY_ID,
            "artifact_id": ARTIFACT_ID,
            "artifact_schema_id": ARTIFACT_SCHEMA_ID,
            "artifact_schema": {"myobj": "mylucabello"},
            "tags": ["t1", "t2", "t1"],
        },
    )
    assert r.status_code == 200
    x = Artifact(**r.json())
    assert isinstance(x, Artifact)


def test_load_artifacts(login):
    for _ in range(20):
        r = client.post(
            "/artifacts",
            headers={"Authorization": f"Bearer {login}"},
            json={
                "name": "ART-" + str(random.randint(000, 999)),
                "account_id": ACCOUNT_ID,
                "opportunity_id": OPPORTUNITY_ID,
                "artifact_schema_id": ARTIFACT_SCHEMA_ID,
                "artifact_schema": {"myobj": random.randint(0000, 9999)},
                "tags": ["t1", "t2", "t1"],
            },
        )

        assert r.status_code == 200


def test_update_artifact(login):
    r = client.put(
        f"/artifacts",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "ART-1",
            "account_id": ACCOUNT_ID,
            "opportunity_id": OPPORTUNITY_ID,
            "artifact_id": ARTIFACT_ID,
            "artifact_schema_id": ARTIFACT_SCHEMA_ID,
            "artifact_schema": {"myobj": "mymatteobello"},
            "tags": ["t1", "t2", "t1"],
        },
    )
    assert r.status_code == 200
    x = Artifact(**r.json())

    # fetch stored account
    r = client.get(
        f"/artifacts/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{ARTIFACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert Artifact(**r.json()) == x
    assert x.artifact_schema == {"myobj": "mymatteobello"}


def test_get_all_artifacts(login):
    r = client.get(
        "/artifacts/",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    l: list[ArtifactOverviewWithAccountName] = [
        ArtifactOverviewWithAccountName(**x) for x in r.json()
    ]
    assert len(l) >= 20


def test_get_all_artifacts_with_filters(login):
    r = client.get(
        "/artifacts/",
        headers={"Authorization": f"Bearer {login}"},
        params={"name": ["ART-1"]},
    )
    assert r.status_code == 200
    l: list[ArtifactOverviewWithAccountName] = [
        ArtifactOverviewWithAccountName(**x) for x in r.json()
    ]
    assert len(l) >= 20


def test_get_all_artifacts_for_account_id(login):
    r = client.get(
        f"/artifacts/{ACCOUNT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[ArtifactOverviewWithOpportunityName] = [
        ArtifactOverviewWithOpportunityName(**x) for x in r.json()
    ]
    assert len(l) >= 20


def test_get_all_artifacts_for_opportunity_id(login):
    r = client.get(
        f"/artifacts/{ACCOUNT_ID}/{OPPORTUNITY_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[ArtifactOverview] = [ArtifactOverview(**x) for x in r.json()]
    assert len(l) >= 20


def test_delete_artifact(login):
    r = client.get(
        f"/artifacts/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{ARTIFACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    acc = Artifact(**r.json())

    r = client.delete(
        f"/artifacts/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{ARTIFACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert acc == Artifact(**r.json())

    # a get returns null
    r = client.get(
        f"/artifacts/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{ARTIFACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # a second delete return null
    r = client.delete(
        f"/artifacts/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{ARTIFACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # recreate account for other tests
    test_create_artifact(login)
