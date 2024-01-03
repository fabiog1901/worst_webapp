import datetime as dt
from typing import Annotated

from fastapi import Depends, HTTPException, status, BackgroundTasks, APIRouter
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import minio
import validators
from minio.deleteobjects import DeleteObject
from apiserver import db
from apiserver.models import UserInDB

# to get a string like this run:
# openssl rand -hex 32
JWT_KEY = os.getenv("JWT_KEY")
JWT_KEY_ALGORITHM = os.getenv("JWT_KEY_ALGORITHM")

if not JWT_KEY or not JWT_KEY_ALGORITHM:
    raise EnvironmentError("JWT_KEY or JWT_KEY_ALGORITHM env variables not found!")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login", scopes={"rw": "rw", "admin": "admin"}
)


S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_USE_SECURE_TLS = (
    True
    if os.getenv("S3_USE_SECURE_TLS", "True").lower()
    in ["true", "1", "t", "y", "yes", "on"]
    else False
)
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PRESIGNED_URL_EXPIRY_SECONDS = int(os.getenv("S3_PRESIGNED_URL_EXPIRY_SECONDS", 5))

minio_client = minio.Minio(
    endpoint=S3_ENDPOINT_URL,
    secure=S3_USE_SECURE_TLS,
    access_key=S3_ACCESS_KEY,
    secret_key=S3_SECRET_KEY,
)


def get_api_router(name: str) -> APIRouter:
    return APIRouter(
        prefix=f"/{name}",
        tags=[name],
    )


def get_presigned_get_url(filename: str) -> str:
    data = minio_client.presigned_get_object(
        S3_BUCKET,
        filename,
        expires=dt.timedelta(seconds=S3_PRESIGNED_URL_EXPIRY_SECONDS),
    )

    if validators.url(data):  # type: ignore
        return data
    else:
        raise ValueError(f"Could not generate presigned-get-url for {filename}")


def get_presigned_put_url(filename: str):
    data = minio_client.presigned_put_object(
        S3_BUCKET,
        filename,
        expires=dt.timedelta(seconds=S3_PRESIGNED_URL_EXPIRY_SECONDS),
    )

    if validators.url(data):  # type: ignore
        return data
    else:
        raise ValueError(f"Could not generate presigned-put-url for {filename}")


def s3_remove_object(filename: str):
    minio_client.remove_object(S3_BUCKET, filename)


def s3_list_all_objects(folder: str) -> list[str]:
    return [
        x.object_name
        for x in minio_client.list_objects(S3_BUCKET, folder, recursive=True)
    ]


def s3_delete_all_objects(folder: str):
    delete_object_list = map(
        lambda x: DeleteObject(x.object_name),
        minio_client.list_objects(S3_BUCKET, folder, recursive=True),
    )

    errors = minio_client.remove_objects(S3_BUCKET, delete_object_list)
    for _ in errors:
        pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> UserInDB | None:
    user: UserInDB = db.get_user_with_hash(username)

    if not user:
        return None
    if user.failed_attempts >= 3:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User is locked. Contact your Administrator.",
        )
    if not verify_password(password, user.hashed_password):
        db.increase_failed_attempt_count(user.user_id)
        return None

    if user.failed_attempts != 0:
        db.reset_failed_attempt_count(user.user_id)

    return user


def create_access_token(data: dict, expire_seconds: int) -> str:
    to_encode = data.copy()
    to_encode.update(
        {"exp": dt.datetime.utcnow() + dt.timedelta(seconds=expire_seconds)}
    )

    try:
        encoded_jwt: str = jwt.encode(to_encode, JWT_KEY, JWT_KEY_ALGORITHM)
    except Exception as e:
        raise e

    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], security_scopes: SecurityScopes
) -> UserInDB:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, JWT_KEY, JWT_KEY_ALGORITHM)
    except (JWTError, Exception):
        raise credentials_exception

    token_username = payload.get("sub", "")
    token_scopes = payload.get("scopes", [])

    if not token_username:
        raise credentials_exception

    user: UserInDB = db.get_user_with_hash(token_username)

    if not user:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Not enough permissions. Missing scopes: {security_scopes.scopes}",
                headers={"WWW-Authenticate": authenticate_value},
            )

    if user.is_disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return user
