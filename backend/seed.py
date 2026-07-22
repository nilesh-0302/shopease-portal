"""Seed the database with sample orders, tickets, and tracking records."""

import asyncio
import os
from datetime import date

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.models import Order, Ticket, Tracking

load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

ORDERS = [
    Order(
        id="ORD001",
        customer="priya.sharma@example.com",
        items=["Wireless Headphones", "USB-C Cable", "Phone Stand"],
        status="shipped",
        total=349900,
    ),
    Order(
        id="ORD002",
        customer="rahul.verma@example.com",
        items=["Running Shoes", "Sports Socks (3-pack)"],
        status="delivered",
        total=289500,
    ),
    Order(
        id="ORD003",
        customer="anita.desai@example.com",
        items=["Yoga Mat", "Resistance Bands", "Water Bottle"],
        status="pending",
        total=159900,
    ),
]

TICKETS = [
    Ticket(
        id="TKT001",
        order_id="ORD001",
        issue="My headphones arrived but one earcup is not working. Requesting a replacement.",
        status="open",
    ),
    Ticket(
        id="TKT002",
        order_id="ORD002",
        issue="Wrong shoe size delivered. Ordered size 9 but received size 8.",
        status="in-progress",
    ),
]

TRACKING = [
    Tracking(
        order_id="ORD001",
        location="Mumbai Sorting Hub",
        eta=date(2026, 6, 4),
    ),
    Tracking(
        order_id="ORD002",
        location="Delivered to doorstep",
        eta=date(2026, 5, 30),
    ),
]


async def seed() -> None:
    """Insert all sample records into the database, skipping existing ones."""
    async with async_session_maker() as session:
        await insert_records(session, ORDERS, "orders")
        await insert_records(session, TICKETS, "tickets")
        await insert_records(session, TRACKING, "tracking")
        await session.commit()
    print("Seeding complete.")


async def insert_records(session: AsyncSession, records: list, label: str) -> None:
    """Add records to the session using merge so re-runs don't fail on duplicates."""
    for record in records:
        await session.merge(record)
    print(f"  Queued {len(records)} {label} record(s).")


if __name__ == "__main__":
    asyncio.run(seed())
