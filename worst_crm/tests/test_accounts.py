from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Account
from  worst_crm.tests.utils import login, setup_test
from uuid import UUID

client = TestClient(app)

# CREATE
def test_get_accounts_non_auth():
    r = client.get("/accounts")

    assert r.status_code == 401


def create_account(token: str) -> Account:
    r = client.post(
        "/accounts",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_acc1",
            "description": "dummy descr",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t11", "t22", "t22"]
        }""",
    )

    assert r.status_code == 200

    return Account(**r.json())


def delete_account(account_id: UUID, token: str, ):
    r = client.delete(
        f"/accounts/{account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert r.status_code == 200
    
    return Account(**r.json())


def test_crud_account(login, setup_test):

    token = login

    # CREATE
    acc = create_account(token)

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
    del_acc = delete_account(acc.account_id, token)

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
