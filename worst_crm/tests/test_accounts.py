from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Account, NewAccount
import worst_crm.tests.test_utils as utils
from pydantic import Json

client = TestClient(app)


def test_get_accounts_non_auth():
    r = client.get("/accounts")

    assert r.status_code == 401


def test_crud_account():
    utils.test_setup()

    token = utils.login()

    assert token is not None

    # CREATE
    r = client.post(
        "/accounts",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_acc1",
            "description": "dummy descr",
            "status": "NEW",
            "tags": ["t1", "t2", "t2"],
            "data": {"k": "v"}
        }""",
    )

    assert r.status_code == 200
    acc = Account(**r.json())

    # READ
    r = client.get(
        f"/accounts/{acc.account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert acc == Account(**r.json())

    r = client.get(
        "/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )

    l: list[Account] = [Account(**x) for x in r.json()]

    assert len(l) > 0

    # UPDATE
    r = client.put(
        f"/accounts/{acc.account_id}",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_acc1",
            "description": "dummy descr UPDATED",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t5555"],
            "data": {"k": "v", "kk": "vv"}
        }""",
    )

    upd_acc = Account(**r.json())

    r = client.get(
        f"/accounts/{acc.account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert upd_acc == Account(**r.json())

    # DELETE
    r = client.delete(
        f"/accounts/{acc.account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    del_acc = Account(**r.json())

    assert del_acc == upd_acc

    # a read returns null
    r = client.get(
        f"/accounts/{acc.account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert r.status_code == 200
    assert r.json() is None

    # a second delete return null
    r = client.delete(
        f"/accounts/{acc.account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert r.status_code == 200
    assert r.json() is None

    utils.test_cleanup()
