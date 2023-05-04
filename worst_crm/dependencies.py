import datetime as dt
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

from worst_crm import db
from worst_crm.models import UserInDB

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


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> UserInDB | None:
    user: UserInDB | None = db.get_user_with_hash(username)

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


async def get_current_active_user(
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

    user: UserInDB | None = db.get_user_with_hash(token_username)

    if not user:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    if user.is_disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return user
