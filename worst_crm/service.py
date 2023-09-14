from uuid import UUID
from worst_crm import db


def get_all(obj_name: str):
    return db.get_all(obj_name)


def get(obj_name: str, id: UUID):
    return db.get(obj_name, id)


def create(obj_name: str, x):
    return db.create(obj_name, x)


def update(obj_name: str, x):
    return db.update(obj_name, x)


def delete(obj_name: str, id: UUID):
    return db.delete(obj_name, id)


def add_attachment(obj_name: str, id: UUID, filename: str):
    print("Mona add_account_attachment")
    return None


def remove_attachment(obj_name: str, id: UUID, filename: str):
    print("Mona remove_account_attachment:")
    return None


def log_event(obj_name: str, username: str, action: str, details: str):
    return db.log_event(obj_name, username, action, details)
