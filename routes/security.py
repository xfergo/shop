from datetime import datetime, timezone, timedelta
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from db import get_customer, get_db
from models import Customer
from schemas import CustomerCreate, CustomerResponse

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

redis_client = aioredis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


async def get_redis():
    yield redis_client


def hash_passwd(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


def create_access_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
) -> Customer:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    redis_key = f"user_session:{email}"

    cached_user = await redis.get(redis_key)
    if cached_user:
        user_schema = CustomerResponse.model_validate_json(cached_user)
        return Customer(**user_schema.model_dump())

    customer = await get_customer(email, session)
    if not customer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user_json = CustomerResponse.model_validate(customer).model_dump_json()
    await redis.setex(
        redis_key,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        user_json
    )

    return customer


@router.post("/token")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
):
    customer = await get_customer(form_data.username, session)

    if not customer or not bcrypt.checkpw(form_data.password.encode("utf-8"), customer.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(customer.email)

    user_json = CustomerResponse.model_validate(customer).model_dump_json()

    await redis.setex(
        f"user_session:{customer.email}",
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        user_json
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=CustomerResponse)
async def registration(
        data: CustomerCreate,
        session: AsyncSession = Depends(get_db),
):
    customer = Customer(**data.model_dump(exclude={"password"}))
    customer.password = hash_passwd(data.password)
    session.add(customer)

    try:
        await session.commit()
        await session.refresh(customer)
        return customer

    except IntegrityError:

        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email has already been taken"
        )