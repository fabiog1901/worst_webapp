from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import (
    Project,
    NewProject,
    ProjectOverview,
    ProjectOverviewWithAccountName,
)
from worst_crm.tests import utils
from worst_crm.tests.utils import login, setup_test
import hashlib
import validators

client = TestClient(app)

new_proj: NewProject
proj: Project


def test_get_projects_non_auth():
    r = client.get("/projects")

    assert r.status_code == 401


def test_create_project(login, setup_test):
    acc = utils.create_account(login)

    global new_proj
    new_proj = utils.create_project(acc.account_id, login)

    assert isinstance(new_proj, NewProject)


def test_update_project(login, setup_test):
    global new_proj
    global proj
    upd_proj = utils.update_project(new_proj.account_id, new_proj.project_id, login)

    assert isinstance(upd_proj, Project)
    assert upd_proj == utils.get_project(
        new_proj.account_id, new_proj.project_id, login
    )

    proj = upd_proj


def test_read_all_projects(login, setup_test):
    for _ in range(50):
        utils.create_project(proj.account_id, login)

    r = client.get(
        "/projects/",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[ProjectOverviewWithAccountName] = [
        ProjectOverviewWithAccountName(**x) for x in r.json()
    ]
    assert len(l) >= 50


def test_read_all_projects_with_filters(login, setup_test):
    r = client.get(
        "/projects/",
        headers={"Authorization": f"Bearer {login}"},
        params={"status": ["ON HOLD"]},
    )
    assert r.status_code == 200
    l: list[ProjectOverviewWithAccountName] = [
        ProjectOverviewWithAccountName(**x) for x in r.json()
    ]
    assert len(l) == 1


def test_read_all_projects_for_account_id(login, setup_test):
    r = client.get(
        f"/projects/{proj.account_id}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[ProjectOverview] = [ProjectOverview(**x) for x in r.json()]
    assert len(l) >= 50


def test_attachment_upload_and_download(login, setup_test):
    global proj

    filename = "1MB with spaces.txt"

    # Uploading
    r = client.get(
        f"/projects/{proj.account_id}/{proj.project_id}/presigned-put-url/{filename}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    assert validators.url(r.text)  # type: ignore
    utils.s3_upload(r.text, f".testdata/{filename}")

    # Downloading
    r = client.get(
        f"/projects/{proj.account_id}/{proj.project_id}/presigned-get-url/{filename}",
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
        f"projects/{proj.account_id}/{proj.project_id}/attachments/{filename}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    proj_with_attachments = utils.get_project(proj.account_id, proj.project_id, login)

    if proj_with_attachments:
        proj = proj_with_attachments


def test_delete_project(login, setup_test):
    del_proj = utils.delete_project(proj.account_id, proj.project_id, login)

    assert del_proj == proj

    # a read returns null
    assert utils.get_project(proj.account_id, proj.project_id, login) is None

    # a second delete return null
    assert utils.delete_project(proj.account_id, proj.project_id, login) is None

    # finally, delete account
    assert utils.delete_account(proj.account_id, login)
