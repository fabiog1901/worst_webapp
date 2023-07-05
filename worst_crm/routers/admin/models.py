from fastapi import APIRouter
from worst_crm import db


router = APIRouter(prefix="/models", tags=["admin/models"])


# ACCOUNT
@router.get("/account")
async def get_account_model() -> dict:
    return db.get_model("account")


@router.put("/account")
async def update_account_model(model: dict) -> dict:
    return db.update_model("account", model)


# OPPORTUNITY
@router.get("/opportunity")
async def get_opportunity_model() -> dict:
    return db.get_model("opportunity")


@router.put("/opportunity")
async def update_opportunity_model(model: dict) -> dict:
    return db.update_model("opportunity", model)


# ARTIFACT
@router.get("/artifact")
async def get_artifact_model() -> dict:
    return db.get_model("artifact")


@router.put("/artifact")
async def update_artifact_model(model: dict) -> dict:
    return db.update_model("artifact", model)


# PROJECT
@router.get("/project")
async def get_project_model() -> dict:
    return db.get_model("project")


@router.put("/project")
async def update_project_model(model: dict) -> dict:
    return db.update_model("project", model)


# TASK
@router.get("/task")
async def get_task_model() -> dict:
    return db.get_model("task")


@router.put("/task")
async def update_task_model(model: dict) -> dict:
    return db.update_model("task", model)


# CONTACT
@router.get("/contact")
async def get_contact_model() -> dict:
    return db.get_model("contact")


@router.put("/contact")
async def update_contact_model(model: dict) -> dict:
    return db.update_model("contact", model)
