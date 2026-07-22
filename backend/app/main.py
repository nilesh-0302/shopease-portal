from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.db import models   # 🔥 required to load models
import logging

from app.routes import auth, cart, customer_profile, notifications, orders, products, tickets, tracking


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


app = FastAPI(title="ShopEase Customer Portal")

# 🔥 ADD THIS BLOCK
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    return {"status":"OK"}

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all
    allow_credentials=False,    # important
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(cart.router)
app.include_router(customer_profile.router)
app.include_router(products.router)
app.include_router(notifications.router)
app.include_router(orders.router)
app.include_router(tickets.router)
app.include_router(tracking.router)