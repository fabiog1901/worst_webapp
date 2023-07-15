from fastapi import Security, BackgroundTasks
from fastapi.responses import HTMLResponse
from typing import Annotated
from uuid import UUID, uuid4
from worst_crm import db
from worst_crm.models import (
    AccountNote,
    AccountNoteInDB,
    AccountNoteOverview,
    NoteFilters,
    OpportunityNote,
    OpportunityNoteInDB,
    OpportunityNoteOverview,
    ProjectNote,
    ProjectNoteInDB,
    ProjectNoteOverview,
    UpdatedAccountNote,
    UpdatedOpportunityNote,
    UpdatedProjectNote,
    User,
)
import worst_crm.dependencies as dep
import inspect

NAME = __name__.split(".")[-1]

router = dep.get_api_router(NAME)


# ACCOUNT_NOTE
@router.get(
    "/account/{account_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_account_notes(
    account_id: UUID,
    note_filters: NoteFilters | None = None,
) -> list[AccountNoteOverview]:
    return db.get_all_account_notes(account_id, note_filters)


@router.get(
    "/account/{account_id}/{note_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_account_note(
    account_id: UUID,
    note_id: UUID,
) -> AccountNote | None:
    return db.get_account_note(account_id, note_id)


@router.post(
    "/account",
    description="`note_id` will be generated if not provided by client.",
)
async def create_account_note(
    acc_note: UpdatedAccountNote,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> AccountNote | None:
    note_in_db = AccountNoteInDB(
        **acc_note.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    if not note_in_db.note_id:
        note_in_db.note_id = uuid4()

    x = db.create_account_note(note_in_db)
    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.put(
    "/account",
)
async def update_account_note(
    note: UpdatedAccountNote,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> AccountNote | None:
    note_in_db = AccountNoteInDB(**note.model_dump(), updated_by=current_user.user_id)

    x = db.update_account_note(note_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.delete(
    "/account/{account_id}/{note_id}",
)
async def delete_account_note(
    account_id: UUID,
    note_id: UUID,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> AccountNote | None:
    x = db.delete_account_note(account_id, note_id)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.get(
    "/account/{account_id}/{note_id}/presigned-get-url/{filename}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_presigned_get_url_for_account_note(
    account_id: UUID,
    note_id: UUID,
    filename: str,
) -> HTMLResponse:
    s3_object_name = str(account_id) + "/" + str(note_id) + "/" + filename
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    "/account/{account_id}/{note_id}/presigned-put-url/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def get_presigned_put_url_for_account_note(
    account_id: UUID,
    note_id: UUID,
    filename: str,
) -> HTMLResponse:
    s3_object_name = str(account_id) + "/" + str(note_id) + "/" + filename
    db.add_account_note_attachment(account_id, note_id, filename)
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    "/account/{account_id}/{note_id}/attachments/{filename}",
)
async def delete_attachement_from_account_note(
    account_id: UUID,
    note_id: UUID,
    filename: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
) -> None:
    s3_object_name = str(account_id) + "/" + str(note_id) + "/" + filename
    db.remove_account_note_attachment(account_id, note_id, filename)
    dep.s3_remove_object(s3_object_name)


# OPPORTUNITY_NOTE
@router.get(
    "/opportunity/{account_id}/{opportunity_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_opportunity_notes(
    account_id: UUID,
    opportunity_id: UUID,
    note_filters: NoteFilters | None = None,
) -> list[OpportunityNoteOverview]:
    return db.get_all_opportunity_notes(account_id, opportunity_id, note_filters)


@router.get(
    "/opportunity/{account_id}/{opportunity_id}/{note_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_opportunity_note(
    account_id: UUID,
    opportunity_id: UUID,
    note_id: UUID,
) -> OpportunityNote | None:
    return db.get_opportunity_note(account_id, opportunity_id, note_id)


@router.post(
    "/opportunity",
    description="`note_id` will be generated if not provided by client.",
)
async def create_opportunity_note(
    note: UpdatedOpportunityNote,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> OpportunityNote | None:
    note_in_db = OpportunityNoteInDB(
        **note.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    if not note_in_db.note_id:
        note_in_db.note_id = uuid4()

    x = db.create_opportunity_note(note_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.put(
    "/opportunity",
)
async def update_opportunity_note(
    note: UpdatedOpportunityNote,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> OpportunityNote | None:
    note_in_db = OpportunityNoteInDB(
        **note.model_dump(), updated_by=current_user.user_id
    )

    x = db.update_opportunity_note(note_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.delete(
    "/opportunity/{account_id}/{opportunity_id}/{note_id}",
)
async def delete_opportunity_note(
    account_id: UUID,
    opportunity_id: UUID,
    note_id: UUID,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> OpportunityNote | None:
    x = db.delete_opportunity_note(account_id, opportunity_id, note_id)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.get(
    "/opportunity/{account_id}/{opportunity_id}/{note_id}/presigned-get-url/{filename}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_presigned_get_url_for_opportunity_note(
    account_id: UUID,
    opportunity_id: UUID,
    note_id: UUID,
    filename: str,
) -> HTMLResponse:
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(note_id)
        + "/"
        + filename
    )
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    "/opportunity/{account_id}/{opportunity_id}/{note_id}/presigned-put-url/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def get_presigned_put_url_for_opportunity_note(
    account_id: UUID,
    opportunity_id: UUID,
    note_id: UUID,
    filename: str,
) -> HTMLResponse:
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(note_id)
        + "/"
        + filename
    )
    db.add_opportunity_note_attachment(account_id, opportunity_id, note_id, filename)
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    "/opportunity/{account_id}/{opportunity_id}/{note_id}/attachments/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_attachement_from_opportunity_note(
    account_id: UUID,
    opportunity_id: UUID,
    note_id: UUID,
    filename: str,
) -> None:
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(note_id)
        + "/"
        + filename
    )
    db.remove_opportunity_note_attachment(account_id, opportunity_id, note_id, filename)
    dep.s3_remove_object(s3_object_name)


# PROJECT_NOTE
@router.get(
    "/project/{account_id}/{opportunity_id}/{project_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_project_notes(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
) -> list[ProjectNoteOverview]:
    return db.get_all_project_notes(account_id, opportunity_id, project_id)


@router.get(
    "/project/{account_id}/{opportunity_id}/{project_id}/{note_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_project_note(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    note_id: UUID,
) -> ProjectNote | None:
    return db.get_project_note(account_id, opportunity_id, project_id, note_id)


@router.post(
    "/project",
    description="`note_id` will be generated if not provided by client.",
)
async def create_project_note(
    note: UpdatedProjectNote,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> ProjectNote | None:
    note_in_db = ProjectNoteInDB(
        **note.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    if not note_in_db.note_id:
        note_in_db.note_id = uuid4()

    x = db.create_project_note(note_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.put(
    "/project",
)
async def update_project_note(
    note: UpdatedProjectNote,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> ProjectNote | None:
    note_in_db = ProjectNoteInDB(
        **note.model_dump(exclude_unset=True), updated_by=current_user.user_id
    )

    x = db.update_project_note(note_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.delete(
    "/project/{account_id}/{opportunity_id}/{project_id}/{note_id}",
)
async def delete_project_note(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    note_id: UUID,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> ProjectNote | None:
    x = db.delete_project_note(account_id, opportunity_id, project_id, note_id)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.get(
    "/project/{account_id}/{opportunity_id}/{project_id}/{note_id}/presigned-get-url/{filename}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_presigned_get_url_for_project_note(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    note_id: UUID,
    filename: str,
) -> HTMLResponse:
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(project_id)
        + "/"
        + str(note_id)
        + "/"
        + filename
    )
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    "/project/{account_id}/{opportunity_id}/{project_id}/{note_id}/presigned-put-url/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def get_presigned_put_url_for_project_note(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    note_id: UUID,
    filename: str,
) -> HTMLResponse:
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(project_id)
        + "/"
        + str(note_id)
        + "/"
        + filename
    )
    db.add_project_note_attachment(
        account_id, opportunity_id, project_id, note_id, filename
    )
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    "/project/{account_id}/{opportunity_id}/{project_id}/{note_id}/attachments/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_attachement_from_project_note(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    note_id: UUID,
    filename: str,
) -> None:
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(project_id)
        + "/"
        + str(note_id)
        + "/"
        + filename
    )
    db.remove_project_note_attachment(
        account_id, opportunity_id, project_id, note_id, filename
    )
    dep.s3_remove_object(s3_object_name)
