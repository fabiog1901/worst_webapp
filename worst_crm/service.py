from uuid import UUID, uuid4
from worst_crm import db
import datetime as dt
from typing import Type
from worst_crm.models import BaseFields
from worst_crm.models import pyd_models, Model, ModelUpdate


def get_all(obj_name: str) -> list[Type[BaseFields]] | None:
    return db.get_all(obj_name)


def get(obj_name: str, id: UUID) -> Type[BaseFields] | None:
    return db.get(obj_name, id)


def create(
    obj_name: str, user_id: str, model: Type[BaseFields]
) -> Type[BaseFields] | None:
    m: Type[BaseFields] = pyd_models[obj_name]["default"](
        **model.model_dump(exclude_unset=True),
        created_by=user_id,
        updated_by=user_id,
        created_at=dt.datetime.utcnow(),
        updated_at=dt.datetime.utcnow(),
    )

    if not m.id:
        m.id = uuid4()

    return db.create(obj_name, m)


def update(
    obj_name: str, user_id: str, model: Type[BaseFields]
) -> Type[BaseFields] | None:
    m: Type[BaseFields] = pyd_models[obj_name]["default"](
        **model.model_dump(exclude_unset=True),
        updated_by=user_id,
        updated_at=dt.datetime.utcnow(),
    )

    return db.update(obj_name, m)


def delete(obj_name: str, id: UUID) -> Type[BaseFields] | None:
    return db.delete(obj_name, id)


def add_attachment(obj_name: str, id: UUID, filename: str):
    print("Mona add_account_attachment")
    return None


def remove_attachment(obj_name: str, id: UUID, filename: str):
    print("Mona remove_account_attachment:")
    return None


def log_event(obj_name: str, ts: dt.datetime, username: str, action: str, details: str):
    return db.log_event(obj_name, ts, username, action, details)


# MODEL
def get_all_models() -> list[Model] | None:
    return db.get_all_models()


def get_model(name: str) -> Model | None:
    return db.get_model(name)


def create_model(
    model: ModelUpdate,
    user_id: str,
) -> Model | None:
    m = Model(
        **model.model_dump(exclude_unset=True),
        created_by=user_id,
        updated_by=user_id,
        created_at=dt.datetime.utcnow(),
        updated_at=dt.datetime.utcnow(),
    )

    return db.create_model(m)


def update_model(
    model: ModelUpdate,
    user_id: str,
) -> Model | None:
    m = Model(
        **model.model_dump(exclude_unset=True),
        updated_by=user_id,
        updated_at=dt.datetime.utcnow(),
    )

    return db.update_model(m)


def delete_model(name: str) -> Model | None:
    return db.delete_model(name)
