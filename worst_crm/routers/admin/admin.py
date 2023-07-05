from fastapi import APIRouter, Security

from worst_crm import dependencies as dep
from . import users, status, models

router = APIRouter(
    prefix="/admin",
    dependencies=[Security(dep.get_current_user, scopes=["admin"])],
)


router.include_router(users.router)
router.include_router(status.router)
router.include_router(models.router)
