from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import joinedload

from models import CartItem, Customer

engine = create_async_engine("sqlite+aiosqlite:///shop.db", echo=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as db:
        yield db


async def get_customer(email: str, session: AsyncSession):
    stmt = select(Customer).where(Customer.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_cart_items(customer_id, session: AsyncSession):
    stmt = (
        select(CartItem)
        .where(CartItem.customer_id == customer_id)
        .options(joinedload(CartItem.product))
    )
    return (await session.execute(stmt)).scalars().all()

async def is_customer_exist(email: str, session: AsyncSession):
    stmt = ()