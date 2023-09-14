from fastapi import APIRouter, BackgroundTasks, Security
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Annotated, Type
from uuid import UUID, uuid4
from worst_crm.models import User
import inspect
import worst_crm.dependencies as dep
import worst_crm.service as svc
import datetime as dt


class Base(BaseModel):
    id: UUID
    name: str
    owned_by: str
    permissions: dict
    tags: set[str]
    created_by: str
    updated_by: str
    created_at: dt.datetime
    updated_at: dt.datetime


class APIRouter(APIRouter):
    def __init__(
        self,
        obj_name: str,
        return_model: Type[Base],
        overview_model: Type[Base],
        model_in_db: Type[Base],
        update_model: Type[Base],
    ) -> None:
        super().__init__(
            prefix=f"/{obj_name}",
            tags=[obj_name],
        )

        @self.get(
            "",
            dependencies=[Security(dep.get_current_user)],
        )
        async def get_all() -> list[overview_model] | None:
            return svc.get_all(obj_name)

        @self.get(
            "/{id}",
            dependencies=[Security(dep.get_current_user)],
        )
        async def get(
            id: UUID,
        ) -> return_model | None:
            return svc.get(obj_name, id)

        @self.post(
            "",
            description="`id` will be generated if not provided by client.",
        )
        async def create(
            model: update_model,
            current_user: Annotated[
                User, Security(dep.get_current_user, scopes=["rw"])
            ],
            bg_task: BackgroundTasks,
        ) -> return_model | None:
            in_db = model_in_db(
                **model.model_dump(exclude_unset=True),
                created_by=current_user.user_id,
                updated_by=current_user.user_id,
                created_at=dt.datetime.utcnow(),
                updated_at=dt.datetime.utcnow(),
            )

            if not in_db.id:
                in_db.id = uuid4()

            x: return_model = svc.create(obj_name, in_db)

            if x:
                bg_task.add_task(
                    svc.log_event,
                    obj_name,
                    current_user.user_id,
                    inspect.currentframe().f_code.co_name,  # type: ignore
                    x.model_dump_json(),
                )

            return x

        @self.put(
            "",
        )
        async def update(
            model: update_model,
            current_user: Annotated[
                User, Security(dep.get_current_user, scopes=["rw"])
            ],
            bg_task: BackgroundTasks,
        ) -> return_model | None:
            in_db = model_in_db(
                **model.model_dump(exclude_unset=True),
                updated_by=current_user.user_id,
                updated_at=dt.datetime.utcnow(),
            )

            x: return_model = svc.update(obj_name, in_db)

            if x:
                bg_task.add_task(
                    svc.log_event,
                    obj_name,
                    current_user.user_id,
                    inspect.currentframe().f_code.co_name,  # type: ignore
                    x.model_dump_json(),
                )

            return x

        @self.delete(
            "/{id}",
        )
        async def delete(
            id: UUID,
            current_user: Annotated[
                User, Security(dep.get_current_user, scopes=["rw"])
            ],
            bg_task: BackgroundTasks,
        ) -> return_model | None:
            x: return_model = svc.delete(obj_name, id)

            if x:
                bg_task.add_task(
                    svc.log_event,
                    obj_name,
                    current_user.user_id,
                    inspect.currentframe().f_code.co_name,  # type: ignore
                    x.model_dump_json(),
                )

            return x

        # Attachements
        @self.get(
            "/{id}/presigned-get-url/{filename}",
            name="Get pre-signed URL for downloading an attachment",
            dependencies=[Security(dep.get_current_user)],
        )
        async def get_presigned_get_url(
            id: UUID,
            filename: str,
        ):
            s3_object_name = "/".join([obj_name, str(id), filename])
            data = dep.get_presigned_get_url(s3_object_name)
            return HTMLResponse(content=data)

        @self.get(
            "/{id}/presigned-put-url/{filename}",
            dependencies=[Security(dep.get_current_user, scopes=["rw"])],
            name="Get pre-signed URL for uploading an attachment",
        )
        async def get_presigned_put_url(
            id: UUID,
            filename: str,
        ):
            s3_object_name = "/".join([obj_name, str(id), filename])
            svc.add_attachment(obj_name, id, filename)
            data = dep.get_presigned_put_url(s3_object_name)
            return HTMLResponse(content=data)

        @self.delete(
            "/{id}/attachments/{filename}",
            dependencies=[Security(dep.get_current_user, scopes=["rw"])],
        )
        async def delete_attachement(
            id: UUID,
            filename: str,
        ):
            s3_object_name = "/".join([obj_name, str(id), filename])
            svc.remove_attachment(obj_name, id, filename)
            dep.s3_remove_object(s3_object_name)
