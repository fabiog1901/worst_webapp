import random
from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Contact
from worst_crm.tests import utils
from worst_crm.tests.utils import login
import hashlib
import validators
from faker import Faker

fake = Faker()


client = TestClient(app)

ACCOUNT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
CONTACT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


def test_get_contacts_non_auth():
    r = client.get("/contacts")

    assert r.status_code == 401


def test_create_contact(login):
    r = client.post(
        "/contacts",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "account_id": ACCOUNT_ID,
            "contact_id": CONTACT_ID,
            "fname": "Fabio",
            "lname": "Ghirardello",
            "email": "fabio@worstcrm.com",
            "telephone_number": "012387656",
            "tags": ["t1", "t2", "t1"],
        },
    )

    assert r.status_code == 200
    opp = Contact(**r.json())
    assert isinstance(opp, Contact)


def test_load_contacts(login):
    for _ in range(10):
        r = client.post(
            "/contacts",
            headers={"Authorization": f"Bearer {login}"},
            json={
                "account_id": ACCOUNT_ID,
                "fname": fake.first_name(),
                "lname": fake.last_name(),
                "email": fake.ascii_safe_email(),
                "telephone_number": fake.phone_number(),
                "tags": ["t1", "t2", "t1"],
            },
        )

        assert r.status_code == 200


def test_update_contact(login):
    r = client.put(
        f"/contacts",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "account_id": ACCOUNT_ID,
            "contact_id": CONTACT_ID,
            "fname": "Fabio",
            "lname": "Ghirardello",
            "email": "fabio@worstcrm.com",
            "telephone_number": "0000",
            "tags": ["t1", "t2", "t1"],
        },
    )
    assert r.status_code == 200
    x = Contact(**r.json())

    # fetch stored opp
    r = client.get(
        f"/contacts/{ACCOUNT_ID}/{CONTACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert Contact(**r.json()) == x
    assert x.telephone_number == "0000"


def test_get_all_contacts(login):
    r = client.get(
        "/contacts/",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    l: list[Contact] = [Contact(**x) for x in r.json()]
    assert len(l) >= 10


def test_delete_contact(login):
    r = client.get(
        f"/contacts/{ACCOUNT_ID}/{CONTACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    acc = Contact(**r.json())

    r = client.delete(
        f"/contacts/{ACCOUNT_ID}/{CONTACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert acc == Contact(**r.json())

    # a get returns null
    r = client.get(
        f"/contacts/{ACCOUNT_ID}/{CONTACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # a second delete return null
    r = client.delete(
        f"/contacts/{ACCOUNT_ID}/{CONTACT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # recreate account for other tests
    test_create_contact(login)
