from fastapi import APIRouter, Security, Body
from typing import Annotated, Any
import apiserver.dependencies as dep
import apiserver.service as svc
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from apiserver.models import TableData

NAME = __name__.split(".", 2)[-1]

router = APIRouter(
    prefix=f"/{NAME}",
    tags=[NAME],
)


@router.post(
    "/report/{name}",
    dependencies=[Security(dep.get_current_user, scopes=["worst_sql_report"])],
    description="Required permission: `worst_sql_report`",
)
async def execute_sql_report(
    name: str,
    bind_params: Annotated[tuple, Body()],
) -> TableData | None:
    return svc.execute_sql_report(name, bind_params)


@router.post(
    "/select",
    dependencies=[Security(dep.get_current_user, scopes=["worst_sql_select"])],
    description="Required permission: `worst_sql_select`",
)
async def execute_sql_select(
    stmt: Annotated[str, Body()],
    bind_params: Annotated[tuple, Body()],
) -> TableData | None:
    return svc.execute_sql_select(stmt, bind_params)


@router.post(
    "/dml",
    dependencies=[Security(dep.get_current_user, scopes=["worst_sql_dml"])],
    description="Required permission: `worst_sql_dml`",
)
async def execute_sql_dml(
    stmt: Annotated[str, Body()],
    bind_params: Annotated[tuple, Body()],
) -> TableData | None:
    return svc.execute_sql_dml(stmt, bind_params)
