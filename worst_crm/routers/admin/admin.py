from fastapi import APIRouter

from . import users, status, models

router = APIRouter(prefix="/admin")


router.include_router(users.router)
# router.include_router(status.router)
router.include_router(models.router)
