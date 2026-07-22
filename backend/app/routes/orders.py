from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import get_current_user, require_admin
from app.db.database import get_db
from app.db.models import Order, User
from app.models.schema import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])


async def fetch_all_orders(db: AsyncSession) -> List[Order]:
    """Query the database and return all orders sorted by newest first."""
    result = await db.execute(select(Order).order_by(Order.created_at.desc()))
    return result.scalars().all()


async def fetch_customer_orders(user_id: int, db: AsyncSession) -> List[Order]:
    """Return all orders belonging to the given user_id."""
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    return result.scalars().all()


async def fetch_user_by_email(email: str, db: AsyncSession):
    """Return a User by email, or None if not found."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def fetch_order_by_id(order_id: str, db: AsyncSession) -> Optional[Order]:
    """Query the database and return a single order by its ID, or None if not found."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def generate_order_id(db: AsyncSession) -> str:
    """Generate the next sequential order ID in the format ORD001, ORD002, etc."""
    result = await db.execute(select(func.count()).select_from(Order))
    count = result.scalar_one()
    return f"ORD{count + 1:03d}"


async def insert_order(data: OrderCreate, user_id: int, db: AsyncSession) -> Order:
    """Persist a new order to the database and return the created instance."""
    order_id = await generate_order_id(db)
    order = Order(
        id=order_id,
        user_id=user_id,
        customer=data.customer,
        items=data.items,
        status=data.status,
        total=data.total,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


VALID_STATUSES = {"shipped", "pending", "delivered", "cancelled"}


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    payload: OrderCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new order — admin only."""
    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Oops! '{payload.status}' isn't a valid status. Please use one of: shipped, pending, delivered, cancelled.",
        )
    customer = await fetch_user_by_email(payload.customer, db)
    if customer is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find a customer account for {payload.customer}. They need to register first.",
        )
    return await insert_order(payload, customer.id, db)


@router.get("/", response_model=List[OrderResponse], status_code=200)
async def get_all_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all orders for admins, or only the caller's orders for customers."""
    if current_user.role == "admin":
        return await fetch_all_orders(db)
    return await fetch_customer_orders(current_user.id, db)


@router.get("/{order_id}", response_model=OrderResponse, status_code=200)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return a single order — admins see any order, customers only see their own."""
    order = await fetch_order_by_id(order_id, db)
    if order is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find your order {order_id}. Please double-check the order ID and try again.",
        )
    if current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view this order. Please contact support if you think this is a mistake.",
        )
    return order
