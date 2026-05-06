from fastapi import FastAPI
import routes.product
import routes.security
import routes.cart
import routes.order


app = FastAPI()
app.include_router(routes.product.router)
app.include_router(routes.security.router)
app.include_router(routes.cart.router, prefix="/cart/items")
app.include_router(routes.order.router, prefix="/orders")
