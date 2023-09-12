from uuid import UUID


def get_all():
    print("Mona get_all: all")
    return None


def get(id: UUID | None = None):
    print("Mona get:", id)
    return None


def create(x):
    print("Mona create:", x)
    return None


def delete():
    print("Mona delete:")
    return None


def update():
    print("Mona update:")
    return None


def add_account_attachment():
    print("Mona add_account_attachment")
    return None


def remove_account_attachment():
    print("Mona remove_account_attachment:")
    return None


def log_event(x, w, e, r):
    print("Mona LogEvent: ", x, w, e, r)
    return None
