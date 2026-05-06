import asyncio
from models import Product, Customer
from db import get_db
import bcrypt

PRODUCTS = [
    ("Shirt", "22.99"),
    ("Shorts", "33.33"),
    ("Pants", "14.44"),
    ("Cap", "22.22"),
    ("Sneakers", "105.99"),
]


def hash_passwd(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


async def seed_db():
    async for session in get_db():
        # --- Products ---
        products = [Product(name=product[0], price=product[1]) for product in PRODUCTS]
        session.add_all(products)


        await session.commit()

    print("Database seeded successfully")


asyncio.run(seed_db())
