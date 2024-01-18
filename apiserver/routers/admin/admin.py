from fastapi import APIRouter

from . import models

router = APIRouter(prefix="/admin")

router.include_router(models.router)
