from fastapi import APIRouter
from worst_crm import db
from worst_crm.models import Status


router = APIRouter(prefix="/status", tags=["admin/status"])


# ACCOUNT
@router.get("/account")
async def get_all_account_status() -> list[Status]:
    return db.get_all_account_status()


@router.post("/account")
async def create_account_status(status: str) -> None:
    return db.create_account_status(status)


@router.delete("/account")
async def delete_account_status(status: str) -> None:
    return db.delete_account_status(status)


# PROJECT
@router.get("/project")
async def get_all_project_status() -> list[Status]:
    return db.get_all_project_status()


@router.post("/project")
async def create_project_status(status: str) -> None:
    return db.create_project_status(status)


@router.delete("/project")
async def delete_project_status(status: str) -> None:
    return db.delete_project_status(status)


# TASK
@router.get("/task")
async def get_all_task_status() -> list[Status]:
    return db.get_all_task_status()


@router.post("/task")
async def create_task_status(status: str) -> None:
    return db.create_task_status(status)


@router.delete("/task")
async def delete_task_status(status: str) -> None:
    return db.delete_task_status(status)
