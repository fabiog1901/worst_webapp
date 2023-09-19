from typing import Type
from uuid import UUID, uuid4
from worst_crm import db
from worst_crm.models import BaseFields, pyd_models, Model, ModelUpdate
import datetime as dt


def get_all(model_name: str) -> list[Type[BaseFields]] | None:
    return db.get_all(model_name)


def get(model_name: str, id: UUID) -> Type[BaseFields] | None:
    return db.get(model_name, id)


def get_all_children(
    model_name: str, id: UUID
) -> dict[str, list[Type[BaseFields]]] | None:
    return db.get_all_children(model_name, id)


def create(
    model_name: str, user_id: str, model: Type[BaseFields]
) -> Type[BaseFields] | None:
    m: Type[BaseFields] = pyd_models[model_name]["default"](
        **model.model_dump(exclude_unset=True),
        created_by=user_id,
        updated_by=user_id,
        created_at=dt.datetime.utcnow(),
        updated_at=dt.datetime.utcnow(),
    )

    if not m.id:
        m.id = uuid4()

    return db.create(model_name, m)


def update(
    model_name: str, user_id: str, model: Type[BaseFields]
) -> Type[BaseFields] | None:
    m = pyd_models[model_name]["default"](
        **model.model_dump(exclude_unset=True),
        updated_by=user_id,
        updated_at=dt.datetime.utcnow(),
    )

    return db.update(model_name, m)


def delete(model_name: str, id: UUID) -> Type[BaseFields] | None:
    return db.delete(model_name, id)


def add_attachment(model_name: str, id: UUID, filename: str):
    print("Mona add_account_attachment")
    return None


def remove_attachment(model_name: str, id: UUID, filename: str):
    print("Mona remove_account_attachment:")
    return None


def log_event(
    model_name: str, ts: dt.datetime, username: str, action: str, details: str
):
    return db.log_event(model_name, ts, username, action, details)


# MODEL
def get_all_models() -> list[Model] | None:
    return db.get_all_models()


def get_model(model_name: str) -> Model | None:
    # TODO sanitize name
    return db.get_model(model_name.lower)


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

    # TODO sanitize incoming name
    m.name = m.name.lower()

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

    # TODO sanitize incoming name
    m.name = m.name.lower()

    return db.update_model(m)


def delete_model(model_name: str) -> Model | None:
    # TODO sanitize name
    return db.delete_model(model_name.lower())
