from typing import Type
from uuid import UUID, uuid4
from apiserver import db
from apiserver.models import BaseFields, pyd_models, Model, ModelUpdate, Report
import datetime as dt
import apiserver.dependencies as dep


def get_all_instances(model_name: str) -> list[Type[BaseFields]] | None:
    return db.get_all_instances(model_name)


def get_instance(
    model_name: str,
    id: UUID,
) -> Type[BaseFields] | None:
    return db.get_instance(model_name, id)


def get_all_children(
    model_name: str,
    id: UUID,
) -> dict[str, list[Type[BaseFields]]] | None:
    return db.get_all_children(model_name, id)


def get_all_children_for_model(
    model_name: str,
    id: UUID,
    children_model_name: str,
) -> list[Type[BaseFields]] | None:
    return db.get_all_children_for_model(model_name, id, children_model_name)


def get_parent_chain(
    model_name: str,
    id: UUID,
) -> list | None:
    raw_list = db.get_parent_chain(model_name, id)

    # [ [ null, null, "acc3" ], [ "account", "3fa85f64-5717-4562-b3fc-2c963f66afa4", "prog3-acc3" ] ]

    l = []
    if raw_list:
        for i in range(len(raw_list) - 1):
            l.append([raw_list[i + 1][0], raw_list[i + 1][1], raw_list[i][2]])

        l.append([model_name, str(id), raw_list[-1][2]])

    return l


def create_instance(
    model_name: str,
    user_id: str,
    model: Type[BaseFields],
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

    return db.create_instance(model_name, m)


def update_instance(
    model_name: str, user_id: str, model: Type[BaseFields]
) -> Type[BaseFields] | None:
    m = pyd_models[model_name]["default"](
        **model.model_dump(exclude_unset=True),
        updated_by=user_id,
        updated_at=dt.datetime.utcnow(),
    )

    return db.update_instance(model_name, m)


def partial_update_instance(
    model_name: str, user_id: str, id: UUID, field: str, value
) -> Type[BaseFields] | None:
    return db.partial_update_instance(
        model_name, user_id, id, field, value, dt.datetime.utcnow()
    )


def delete_instance(model_name: str, id: UUID) -> Type[BaseFields] | None:
    # delete all attachments from the instance
    s3_folder_name = "/".join([model_name, str(id)])
    dep.s3_delete_all_objects(s3_folder_name)

    # set parent_type and parent_id to NULL for all children
    db.set_parent_to_null(model_name, str(id))

    # finally, delete the instance itself
    return db.delete_instance(model_name, id)


def add_attachment(model_name: str, id: UUID, filename: str):
    return db.add_attachment(model_name, id, filename)


def remove_attachment(model_name: str, id: UUID, filename: str):
    return db.remove_attachment(model_name, id, filename)


def log_event(
    model_name: str, ts: dt.datetime, username: str, action: str, details: str
):
    return db.log_event(model_name, ts, username, action, details)


# MODEL
def get_all_models() -> dict[str, Model] | None:
    models = db.get_all_models()

    m = {}

    for x in models:
        m[x.name] = x.model_dump(exclude="name")

    return m


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


# REPORTS
def get_all_reports() -> dict[str, Report] | None:
    reports = db.get_all_reports()

    x = {}

    for r in reports:
        x[r.name] = r.model_dump(exclude="name")

    return x


def get_report(name: str) -> Report | None:
    return db.get_report(name)


def create_report(
    name: str,
    sql_stmt: str,
    user_id: str,
) -> Report | None:
    r = Report(
        name=name,
        sql_stmt=sql_stmt,
        created_by=user_id,
        updated_by=user_id,
        created_at=dt.datetime.utcnow(),
        updated_at=dt.datetime.utcnow(),
    )

    return db.create_report(r)


def update_report(
    name: str,
    sql_stmt: str,
    user_id: str,
) -> Report | None:
    r = Report(
        name=name,
        sql_stmt=sql_stmt,
        updated_by=user_id,
        updated_at=dt.datetime.utcnow(),
    )

    return db.update_report(r)


def delete_report(name: str) -> Report | None:
    return db.delete_report(name)
