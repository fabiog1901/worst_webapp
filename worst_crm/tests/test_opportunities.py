from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import (
    Opportunity,
    OpportunityOverview,
    OpportunityOverviewWithAccountName,
)
from worst_crm.tests import utils
from worst_crm.tests.utils import login, setup_test
import hashlib
import validators
from faker import Faker

fake = Faker()


client = TestClient(app)

ACCOUNT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
OPPORTUNITY_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


def test_get_opportunities_non_auth():
    r = client.get("/opportunities")

    assert r.status_code == 401


def test_create_opportunity(login):
    r = client.post(
        "/opportunities",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "OPP-1",
            "account_id": ACCOUNT_ID,
            "opportunity_id": OPPORTUNITY_ID,
            "text": "Initial text",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t1"],
        },
    )

    assert r.status_code == 200
    opp = Opportunity(**r.json())
    assert isinstance(opp, Opportunity)


def test_load_opportunities(login):
    for _ in range(100):
        r = client.post(
            "/opportunities",
            headers={"Authorization": f"Bearer {login}"},
            json={
                "name": "OPP-" + fake.safe_color_name(),
                "account_id": ACCOUNT_ID,
                "text": fake.text(),
                "status": "NEW",
                "due_date": fake.date(),
                "owned_by": "dummyadmin",
                "tags": ["t1", "t2", "t1"],
            },
        )

        assert r.status_code == 200


def test_update_opportunity(login):
    r = client.put(
        f"/accounts",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "OPP-1",
            "account_id": ACCOUNT_ID,
            "opportunity_id": OPPORTUNITY_ID,
            "text": "Updated text",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t1"],
        },
    )
    assert r.status_code == 200
    x = Opportunity(**r.json())

    # fetch stored account
    r = client.get(
        f"/accounts/{ACCOUNT_ID}", headers={"Authorization": f"Bearer {login}"}
    )

    assert r.status_code == 200
    upd_opp = Opportunity(**r.json())

    assert upd_opp == x
    assert x.text == "Updated text"


def test_get_all_opportunities(login):
    r = client.get(
        "/opportunities/",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    l: list[OpportunityOverviewWithAccountName] = [
        OpportunityOverviewWithAccountName(**x) for x in r.json()
    ]
    assert len(l) >= 100


def test_get_all_opportunities_with_filters(login):
    r = client.request(
        "GET",
        "/opportunities/",
        headers={"Authorization": f"Bearer {login}"},
        json={"name": ["OPP-1"]},
    )
    assert r.status_code == 200
    l: list[OpportunityOverviewWithAccountName] = [
        OpportunityOverviewWithAccountName(**x) for x in r.json()
    ]
    assert len(l) == 1


def test_get_all_opportunities_for_account_id(login):
    r = client.get(
        f"/opportunities/{ACCOUNT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[OpportunityOverview] = [OpportunityOverview(**x) for x in r.json()]
    assert len(l) >= 100


def test_attachment_upload_and_download(login):
    for filename in ["1MB with spaces.txt", "ss.png"]:
        # uploading
        r = client.get(
            f"/opportunities/{ACCOUNT_ID}/{OPPORTUNITY_ID}/presigned-put-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        assert validators.url(r.text)  # type: ignore

        utils.s3_upload(r.text, f".testdata/{filename}")

        # Downloading
        r = client.get(
            f"/opportunities/{ACCOUNT_ID}/{OPPORTUNITY_ID}/presigned-get-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        assert validators.url(r.text)  # type: ignore

        utils.s3_download(r.text, f".testdata/.{filename}")

        # comparing for equality
        with open(f".testdata/{filename}", "rb") as f:
            digest1 = hashlib.file_digest(f, "sha256")

        with open(f".testdata/.{filename}", "rb") as f:
            digest2 = hashlib.file_digest(f, "sha256")  # type: ignore

        assert digest1.hexdigest() == digest2.hexdigest()

        # deleting attachment
        r = client.delete(
            f"opportunities/{ACCOUNT_ID}/{OPPORTUNITY_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        # deleting attachment twice
        r = client.delete(
            f"opportunities/{ACCOUNT_ID}/{OPPORTUNITY_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200


def test_delete_opportunity(login):
    r = client.get(
        f"/opportunities/{ACCOUNT_ID}/{OPPORTUNITY_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    acc = Opportunity(**r.json())

    r = client.delete(
        f"/opportunities/{ACCOUNT_ID}/{OPPORTUNITY_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert acc == Opportunity(**r.json())

    # a get returns null
    r = client.get(
        f"/opportunities/{ACCOUNT_ID}/{OPPORTUNITY_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # a second delete return null
    r = client.delete(
        f"/opportunities/{ACCOUNT_ID}/{OPPORTUNITY_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # recreate account for other tests
    test_create_opportunity(login)
