from fastapi import APIRouter

from . import reports, models

router = APIRouter(prefix="/admin")

router.include_router(models.router)
router.include_router(reports.router)
