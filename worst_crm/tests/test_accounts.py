from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Account, AccountOverview
from worst_crm.tests import utils
from worst_crm.tests.utils import login, setup_test
import hashlib
import validators


client = TestClient(app)

acc: Account


def test_get_accounts_non_auth(login, setup_test):
    r = client.get("/accounts")

    assert r.status_code == 401


def test_create_account(login, setup_test):
    global acc
    acc = utils.create_account(login)

    assert isinstance(acc, Account)


def test_update_account(login, setup_test):
    global acc
    upd_acc = utils.update_account(acc.account_id, login)
    assert isinstance(upd_acc, Account)
    assert upd_acc == utils.get_account(acc.account_id, login)

    acc = upd_acc


def test_read_all_accounts(login, setup_test):
    for _ in range(50):
        utils.create_account(login)

    # READ ALL
    r = client.get(
        "/accounts",
        headers={"Authorization": f"Bearer {login}"},
    )

    l: list[AccountOverview] = [AccountOverview(**x) for x in r.json()]

    assert r.status_code == 200
    assert len(l) >= 50


def test_read_all_accounts_with_filters(login, setup_test):
    r = client.get(
        "/accounts",
        headers={"Authorization": f"Bearer {login}"},
        params={
            "name": [acc.name],
        },
    )
    assert r.status_code == 200
    l: list[AccountOverview] = [AccountOverview(**x) for x in r.json()]
    assert len(l) == 1


def test_attachment_upload_and_download(login, setup_test):
    global acc

    for filename in ["1MB with spaces.txt", "ss.png"]:
        # uploading
        r = client.get(
            f"/accounts/{acc.account_id}/presigned-put-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        assert validators.url(r.text)  # type: ignore

        utils.s3_upload(r.text, f".testdata/{filename}")

        # Downloading
        r = client.get(
            f"/accounts/{acc.account_id}/presigned-get-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        assert validators.url(r.text)  # type: ignore

        utils.s3_download(r.text, f".testdata/.{filename}")

        # comparing for equality
        with open(f".testdata/{filename}", "rb") as f:
            digest1 = hashlib.file_digest(f, "sha256")

        with open(f".testdata/.{filename}", "rb") as f:
            digest2 = hashlib.file_digest(f, "sha256")

        assert digest1.hexdigest() == digest2.hexdigest()

        # deleting attachment
        r = client.delete(
            f"accounts/{acc.account_id}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        # deleting attachment twice
        r = client.delete(
            f"accounts/{acc.account_id}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

    acc_with_attachments = utils.get_account(acc.account_id, login)

    if acc_with_attachments:
        acc = acc_with_attachments


def test_delete_account(login):
    del_acc = utils.delete_account(acc.account_id, login)

    assert del_acc == acc

    # a read returns null
    assert utils.get_account(acc.account_id, login) is None

    # a second delete return null
    assert utils.delete_account(acc.account_id, login) is None
