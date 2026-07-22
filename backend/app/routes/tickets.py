from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import get_current_user, require_admin, require_customer
from app.db.database import get_db
from app.db.models import Order, Ticket, User
from app.models.schema import TicketCreate, TicketResponse
from app.routes.notifications import insert_notification

router = APIRouter(prefix="/tickets", tags=["tickets"])


async def fetch_all_tickets(db: AsyncSession) -> List[Ticket]:
    """Query the database and return all tickets sorted by newest first."""
    result = await db.execute(select(Ticket).order_by(Ticket.created_at.desc()))
    return result.scalars().all()


async def fetch_customer_tickets(user_id: int, db: AsyncSession) -> List[Ticket]:
    """Return tickets raised against orders belonging to the given user_id."""
    result = await db.execute(
        select(Ticket)
        .join(Order, Ticket.order_id == Order.id)
        .where(Order.user_id == user_id)
        .order_by(Ticket.created_at.desc())
    )
    return result.scalars().all()


async def fetch_order(order_id: str, db: AsyncSession):
    """Return a single order by ID, or None if not found."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def generate_ticket_id(db: AsyncSession) -> str:
    """Generate the next sequential ticket ID in the format TKT001."""
    result = await db.execute(select(func.count()).select_from(Ticket))
    count = result.scalar()
    return f"TKT{count + 1:03d}"


async def insert_ticket(ticket_id: str, data: TicketCreate, db: AsyncSession) -> Ticket:
    """Insert a new ticket into the database and return the created record."""
    ticket = Ticket(
        id=ticket_id,
        order_id=data.order_id,
        issue=data.issue,
        status="open",
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.get("/", response_model=List[TicketResponse], status_code=200)
async def get_all_tickets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all tickets for admins, or the caller's own tickets for customers."""
    if current_user.role == "admin":
        return await fetch_all_tickets(db)
    return await fetch_customer_tickets(current_user.id, db)


@router.post("/", response_model=TicketResponse, status_code=201)
async def create_ticket(
    data: TicketCreate,
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db),
):
    """Create a support ticket — customers only, and only for their own orders."""
    order = await fetch_order(data.order_id, db)
    if order is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find order {data.order_id}. Please double-check the order ID and try again.",
        )
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only raise support tickets for your own orders. Please contact support if you need help.",
        )
    ticket_id = await generate_ticket_id(db)
    ticket = await insert_ticket(ticket_id, data, db)
    message = f"New ticket {ticket_id} raised by {current_user.email}: {data.issue}"
    await insert_notification(message, db)
    return ticket
