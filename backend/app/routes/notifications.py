from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import require_admin
from app.db.database import get_db
from app.db.models import Notification, User
from app.models.schema import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


async def fetch_all_notifications(db: AsyncSession) -> List[Notification]:
    """Return all notifications sorted newest first."""
    result = await db.execute(
        select(Notification).order_by(Notification.created_at.desc())
    )
    return result.scalars().all()


async def fetch_notification_by_id(notif_id: int, db: AsyncSession) -> Optional[Notification]:
    """Return a single notification by ID, or None if not found."""
    result = await db.execute(select(Notification).where(Notification.id == notif_id))
    return result.scalar_one_or_none()


async def insert_notification(message: str, db: AsyncSession) -> Notification:
    """Insert a new notification record and return the saved instance."""
    notif = Notification(message=message)
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif


@router.get("/", response_model=List[NotificationResponse], status_code=200)
async def get_all_notifications(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Return all notifications newest first — admin only."""
    return await fetch_all_notifications(db)


@router.put("/{notif_id}/read", response_model=NotificationResponse, status_code=200)
async def mark_notification_read(
    notif_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read — admin only."""
    notif = await fetch_notification_by_id(notif_id, db)
    if notif is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find notification {notif_id}. Please double-check the ID and try again.",
        )
    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return notif
