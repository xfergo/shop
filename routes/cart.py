from decimal import Decimal
from fastapi import Depends, HTTPException, APIRouter, status
import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db, get_cart_items
from models import Customer, CartItem
from schemas import Cart, CartItem as CartItemSchema
from .security import get_current_user
from redis_schemas import Cart as RedisCart, CartItem as RedisCartItem

from services.cart_service import CartService

router = APIRouter()
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


@router.post("/")
async def add_to_cart(
    product_id: int,
    quantity: int,
    customer: Customer = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),


):
    #service_cache = CartService(r=r)
    #service_cache.add_to_redis(customer.id, product_id, quantity)
    service_db = CartService(db=db)
    return await service_db.add_to_db(
        customer_id=customer.id,
        product_id=product_id,
        quantity=quantity
    )



@router.get("/", response_model=Cart)
async def show_cart(
    customer: Customer = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    #cart_items = CartService(r=r)
    #return await cart_items.get_from_redis(customer.id)

    cart_items = CartService(db=db)

    return await cart_items.get_from_db(customer.id)
