import os
from decimal import Decimal

from fastapi import Depends, HTTPException, APIRouter, status
import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from db import get_db, get_cart_items
from models import Customer, CartItem
from schemas import Cart, CartItem as CartItemSchema
from routes.security import get_current_user
from redis_schemas import Cart as RedisCart, CartItem as RedisCartItem
from sqlalchemy import select
from models import CartItem


load_dotenv()
REDIS_PREFIX = os.environ["REDIS_PREFIX"]


class CartService:
    def __init__(self, db: AsyncSession | None = None, r:redis.Redis | None = None):
        self.db = db
        self.r = r

    async def add_to_db(self, customer_id: int, product_id: int, quantity: int):
        stmt = select(CartItem).where(
             CartItem.customer_id == customer_id,
             CartItem.product_id == product_id
        )

        result = await self.db.execute(stmt)
        item = result.scalar()

        if item:
            item.quantity += quantity
        else:
            item = CartItem(
                customer_id=customer_id,
                product_id=product_id,
                quantity=quantity
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def add_to_redis(self, customer_id: int, product_id: int, quantity: int):
        key = REDIS_PREFIX + str(customer_id)
        cart_item_json: str | None = await self.r.hget(key, str(product_id))
        print(cart_item_json)
        if cart_item_json:
            cart_item = RedisCartItem.model_validate_json(cart_item_json)
            cart_item.quantity += quantity
        else:
            cart_item = RedisCartItem(product_id = product_id, quantity=quantity)
        await self.r.hset(key, str(product_id), cart_item.model_dump_json())
        return cart_item

    async def get_from_db(self, customer_id: int):
        cart_items = await get_cart_items(customer_id, self.db)
        total_price = sum((item.subtotal for item in cart_items), Decimal(0))
        return Cart(
            cart_items=[CartItemSchema.model_validate(item) for item in cart_items],
            total_price=total_price,
        )

    async def get_from_redis(self, customer_id: int) -> Cart:
        key = REDIS_PREFIX + str(customer_id)

        cart_data: dict = await self.r.hgetall(key)

        cart_items = []

        for product_id_str, item_json in cart_data.items():
            redis_item = RedisCartItem.model_validate_json(item_json)

            schema_item = CartItemSchema.model_validate(redis_item.model_dump())
            cart_items.append(schema_item)

        return Cart(
            cart_items=cart_items
        )
