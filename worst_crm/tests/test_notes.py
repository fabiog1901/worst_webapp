import time
from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Note, NewNote, NoteOverviewWithProjectName, NoteOverview
from worst_crm.tests import utils
from worst_crm.tests.utils import login, setup_test
import hashlib
import validators

client = TestClient(app)

new_note: NewNote
note: Note


# CREATE
def test_get_notes_non_auth():
    r = client.get("/notes/123456")

    assert r.status_code == 401


def test_create_note(login, setup_test):
    acc = utils.create_account(login)
    proj = utils.create_project(acc.account_id, login)

    global new_note

    new_note = utils.create_note(proj.account_id, proj.project_id, login)

    assert isinstance(new_note, NewNote)


def test_update_note(login, setup_test):
    global note
    global new_note

    upd_note = utils.update_note(
        new_note.account_id, new_note.project_id, new_note.note_id, login
    )

    assert isinstance(upd_note, Note)
    assert upd_note == utils.get_note(
        new_note.account_id, new_note.project_id, new_note.note_id, login
    )

    note = upd_note


def test_read_all_notes_for_account_id(login, setup_test):
    for _ in range(20):
        time.sleep(1)
        utils.create_note(note.account_id, note.project_id, login)

    r = client.get(
        f"/notes/{note.account_id}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[NoteOverviewWithProjectName] = [
        NoteOverviewWithProjectName(**x) for x in r.json()
    ]
    assert len(l) >= 20


def test_read_all_notes_for_account_id_with_filters(login, setup_test):
    r = client.get(
        f"/notes/{note.account_id}",
        headers={"Authorization": f"Bearer {login}"},
        params={"name": ["NOTE-000001"]},
    )
    assert r.status_code == 200
    l: list[NoteOverviewWithProjectName] = [
        NoteOverviewWithProjectName(**x) for x in r.json()
    ]
    assert len(l) == 1


def test_read_all_notes_for_project_id(login, setup_test):
    r = client.get(
        f"/notes/{note.account_id}/{note.project_id}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[NoteOverview] = [NoteOverview(**x) for x in r.json()]
    assert len(l) >= 1


def test_attachment_upload_and_download(login, setup_test):
    global note

    filename = "1MB with spaces.txt"

    # uploading
    r = client.get(
        f"/notes/{note.account_id}/{note.project_id}/{note.note_id}/presigned-put-url/{filename}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    assert validators.url(r.text)  # type: ignore
    utils.s3_upload(r.text, f".testdata/{filename}")

    # Downloading
    r = client.get(
        f"/notes/{note.account_id}/{note.project_id}/{note.note_id}/presigned-get-url/{filename}",
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
        f"notes/{note.account_id}/{note.project_id}/{note.note_id}/attachments/{filename}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    note_with_attachments = utils.get_note(
        note.account_id, note.project_id, note.note_id, login
    )

    if note_with_attachments:
        note = note_with_attachments


def test_delete_note(login, setup_test):
    del_note = utils.delete_note(note.account_id, note.project_id, note.note_id, login)

    assert del_note == note

    # a read returns null
    assert utils.get_note(note.account_id, note.project_id, note.note_id, login) is None

    # a second delete return null
    assert (
        utils.delete_note(note.account_id, note.project_id, note.note_id, login) is None
    )

    # finally, delete account
    assert utils.delete_project(note.account_id, note.project_id, login)
    assert utils.delete_account(note.account_id, login)
