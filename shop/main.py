from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routes.product
import routes.security
import routes.cart
import routes.order



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.product.router)
app.include_router(routes.security.router)
app.include_router(routes.cart.router, prefix="/cart/items")
app.include_router(routes.order.router, prefix="/orders")
