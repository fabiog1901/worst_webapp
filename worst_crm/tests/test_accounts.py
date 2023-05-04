from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Account, NewAccount
from worst_crm.tests.test_admin_users import login

client = TestClient(app)


def test_get_accounts_non_auth():
    r = client.get("/accounts")

    assert r.status_code == 401


def test_crud_account():
    token = login()

    # CREATE
    r = client.post(
        "/accounts",
        headers={"Authorization": f"Bearer {token}"},
        content=NewAccount(
                account_name="dummy_acc1",
                description="dummy_acc_descr",
                tags=["tag1", "tag2", "tag3", "tag3"],
            ).json(),
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
        content=NewAccount(
            account_name="dummy_acc1",
            description="updated dummy_acc_descr",
            tags=["tag1", "tag2", "tag3", "tag4"],
        ).json(),
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
