from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import get_current_user, require_admin
from app.db.database import get_db
from app.db.models import Order, Tracking, User
from app.models.schema import TrackingCreate, TrackingResponse

router = APIRouter(prefix="/tracking", tags=["tracking"])


async def fetch_tracking(order_id: str, db: AsyncSession):
    """Return the tracking record for an order, or None if not found."""
    result = await db.execute(select(Tracking).where(Tracking.order_id == order_id))
    return result.scalar_one_or_none()


async def fetch_order(order_id: str, db: AsyncSession):
    """Return the order record for the given ID, or None if it doesn't exist."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def insert_tracking(data: TrackingCreate, db: AsyncSession) -> Tracking:
    """Persist a new tracking record and return the created instance."""
    tracking = Tracking(
        order_id=data.order_id,
        location=data.location,
        eta=data.eta,
    )
    db.add(tracking)
    await db.commit()
    await db.refresh(tracking)
    return tracking


@router.post("/", response_model=TrackingResponse, status_code=201)
async def create_tracking(
    payload: TrackingCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Add tracking info for an order — admin only."""
    if not await fetch_order(payload.order_id, db):
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find order {payload.order_id}. Please double-check the order ID and try again.",
        )
    if await fetch_tracking(payload.order_id, db):
        raise HTTPException(
            status_code=400,
            detail=f"Tracking info for order {payload.order_id} already exists. Please contact support to update it.",
        )
    return await insert_tracking(payload, db)


@router.get("/{order_id}", response_model=TrackingResponse, status_code=200)
async def get_tracking(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return tracking info — admins see any order's tracking, customers see only their own."""
    tracking = await fetch_tracking(order_id, db)
    if tracking is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find tracking info for order {order_id}. It may still be processing — please check back soon!",
        )
    if current_user.role != "admin":
        order = await fetch_order(order_id, db)
        if order is None or order.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to view tracking for this order.",
            )
    return tracking
