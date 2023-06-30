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

client = TestClient(app)


def test_get_Opportunitys_non_auth():
    r = client.get("/Opportunitys")

    assert r.status_code == 401


def test_create_Opportunity(login, setup_test):
    acc = utils.create_account(login)

    global new_proj
    new_proj = utils.create_Opportunity(acc.account_id, login)

    assert isinstance(new_proj, NewOpportunity)


def test_update_Opportunity(login, setup_test):
    global new_proj
    global proj
    upd_proj = utils.update_Opportunity(
        new_proj.account_id, new_proj.Opportunity_id, login
    )

    assert isinstance(upd_proj, Opportunity)
    assert upd_proj == utils.get_Opportunity(
        new_proj.account_id, new_proj.Opportunity_id, login
    )

    proj = upd_proj


def test_read_all_Opportunitys(login, setup_test):
    for _ in range(50):
        utils.create_Opportunity(proj.account_id, login)

    r = client.get(
        "/Opportunitys/",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[OpportunityOverviewWithOpportunityName] = [
        OpportunityOverviewWithOpportunityName(**x) for x in r.json()
    ]
    assert len(l) >= 50


def test_read_all_Opportunitys_with_filters(login, setup_test):
    r = client.get(
        "/Opportunitys/",
        headers={"Authorization": f"Bearer {login}"},
        params={"status": ["ON HOLD"]},
    )
    assert r.status_code == 200
    l: list[OpportunityOverviewWithOpportunityName] = [
        OpportunityOverviewWithOpportunityName(**x) for x in r.json()
    ]
    assert len(l) == 1


def test_read_all_Opportunitys_for_account_id(login, setup_test):
    r = client.get(
        f"/Opportunitys/{proj.account_id}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[OpportunityOverview] = [OpportunityOverview(**x) for x in r.json()]
    assert len(l) >= 50


def test_attachment_upload_and_download(login, setup_test):
    global proj

    filename = "1MB with spaces.txt"

    # Uploading
    r = client.get(
        f"/Opportunitys/{proj.account_id}/{proj.Opportunity_id}/presigned-put-url/{filename}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    assert validators.url(r.text)  # type: ignore
    utils.s3_upload(r.text, f".testdata/{filename}")

    # Downloading
    r = client.get(
        f"/Opportunitys/{proj.account_id}/{proj.Opportunity_id}/presigned-get-url/{filename}",
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

    # deleting
    r = client.delete(
        f"Opportunitys/{proj.account_id}/{proj.Opportunity_id}/attachments/{filename}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    proj_with_attachments = utils.get_Opportunity(
        proj.account_id, proj.Opportunity_id, login
    )

    if proj_with_attachments:
        proj = proj_with_attachments


def test_delete_Opportunity(login, setup_test):
    del_proj = utils.delete_Opportunity(proj.account_id, proj.Opportunity_id, login)

    assert del_proj == proj

    # a read returns null
    assert utils.get_Opportunity(proj.account_id, proj.Opportunity_id, login) is None

    # a second delete return null
    assert utils.delete_Opportunity(proj.account_id, proj.Opportunity_id, login) is None

    # finally, delete account
    assert utils.delete_account(proj.account_id, login)
