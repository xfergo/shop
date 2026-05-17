from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Annotated

Currency = Annotated[Decimal, Field(max_digits=10, decimal_places=2, ge=0)]


class CartItem(BaseModel):
    model_config = {"from_attributes": True}
    # price: Currency
    product_id: int
    quantity: int = Field(ge=0)


class Cart(BaseModel):
    cart_items: list[CartItem]


class CustomerCreate(BaseModel):
    name: str
    email: str
    password: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    password: str
    model_config = {"from_attributes": True}