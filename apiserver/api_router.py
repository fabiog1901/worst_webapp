from fastapi import APIRouter, BackgroundTasks, Security
from fastapi.responses import HTMLResponse
from typing import Annotated, Type
from uuid import UUID
from apiserver.models import User, BaseFields
import inspect
import apiserver.dependencies as dep
import apiserver.service as svc
import datetime as dt


class WorstRouter(APIRouter):
    def __init__(
        self,
        model_name: str,
        default_model: Type[BaseFields],
        overview_model: Type[BaseFields],
        update_model: Type[BaseFields],
    ) -> None:
        super().__init__(
            prefix=f"/{model_name}",
            tags=[model_name],
        )

        @self.get(
            "",
            dependencies=[Security(dep.get_current_user)],
        )
        async def get_all() -> list[overview_model] | None:
            return svc.get_all(model_name)

        @self.get(
            "/{id}",
            dependencies=[Security(dep.get_current_user)],
        )
        async def get(
            id: UUID,
        ) -> default_model | None:
            return svc.get(model_name, id)

        @self.get(
            "/{id}/children",
            dependencies=[Security(dep.get_current_user)],
        )
        async def get_all_children(
            id: UUID,
        ) -> dict | None:
            return svc.get_all_children(model_name, id)

        @self.get(
            "/{id}/parent_chain",
            dependencies=[Security(dep.get_current_user)],
        )
        async def get_parent_chain(
            id: UUID,
        ) -> list | None:
            return svc.get_parent_chain(model_name, id)

        @self.get(
            "/{id}/attachment-list",
            dependencies=[Security(dep.get_current_user, scopes=["rw"])],
            name="Get list of all objects in a folder",
        )
        async def get_attachment_list(
            id: UUID,
        ) -> list[str] | None:
            s3_folder_name = "/".join([model_name, str(id)])
            return dep.s3_list_all_objects(s3_folder_name)

        @self.get(
            "/{id}/{children_model_name}",
            dependencies=[Security(dep.get_current_user)],
        )
        async def get_all_children_for_model(
            id: UUID,
            children_model_name: str,
        ) -> list | None:
            return svc.get_all_children_for_model(model_name, id, children_model_name)

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
        ) -> default_model | None:
            x = svc.create(model_name, current_user.user_id, model)

            if x:
                bg_task.add_task(
                    svc.log_event,
                    model_name,
                    dt.datetime.utcnow(),
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
        ) -> default_model | None:
            x = svc.update(model_name, current_user.user_id, model)

            if x:
                bg_task.add_task(
                    svc.log_event,
                    model_name,
                    dt.datetime.utcnow(),
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
        ) -> default_model | None:
            x: default_model = svc.delete(model_name, id)

            if x:
                bg_task.add_task(
                    svc.log_event,
                    model_name,
                    dt.datetime.utcnow(),
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
            s3_object_name = "/".join([model_name, str(id), filename])
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
            s3_object_name = "/".join([model_name, str(id), filename])
            svc.add_attachment(model_name, id, filename)
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
            s3_object_name = "/".join([model_name, str(id), filename])
            svc.remove_attachment(model_name, id, filename)
            dep.s3_remove_object(s3_object_name)
