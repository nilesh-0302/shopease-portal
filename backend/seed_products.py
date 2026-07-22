"""Seed the database with stationery products."""

import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.models import Product

load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"), echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

PRODUCTS = [
    Product(
        id="PROD001",
        name="Ballpoint Pens (Pack of 10)",
        description="Smooth-writing blue ballpoint pens. Comfortable grip, ideal for everyday writing.",
        price=15000,
        category="Pens & Pencils",
        stock=200,
    ),
    Product(
        id="PROD002",
        name="Gel Pens (Pack of 12)",
        description="Vibrant gel ink pens in assorted colours. Great for notes and highlights.",
        price=29900,
        category="Pens & Pencils",
        stock=180,
    ),
    Product(
        id="PROD003",
        name="Pencil Set — HB (Pack of 12)",
        description="Classic HB graphite pencils, pre-sharpened. Suitable for writing and sketching.",
        price=8900,
        category="Pens & Pencils",
        stock=300,
    ),
    Product(
        id="PROD004",
        name="A4 Ruled Notebook (200 pages)",
        description="Single-line ruled notebook with thick 70 GSM pages. Perfect for lectures and journals.",
        price=12000,
        category="Notebooks",
        stock=150,
    ),
    Product(
        id="PROD005",
        name="Spiral Hardcover Notebook (160 pages)",
        description="Durable hardcover with a lay-flat spiral binding. A5 size, dotted pages.",
        price=24900,
        category="Notebooks",
        stock=120,
    ),
    Product(
        id="PROD006",
        name="Sticky Notes — 5 Colour Pack (100 sheets each)",
        description="Pastel-coloured sticky notes. Easy to peel, repositionable, and residue-free.",
        price=25000,
        category="Organisation",
        stock=250,
    ),
    Product(
        id="PROD007",
        name="Highlighter Set (5 colours)",
        description="Chisel-tip highlighters in yellow, pink, blue, green, and orange. Smear-resistant ink.",
        price=19900,
        category="Pens & Pencils",
        stock=220,
    ),
    Product(
        id="PROD008",
        name="Stapler with 1000 Pins",
        description="Full-strip stapler handles up to 25 sheets. Includes 1000 standard 26/6 staple pins.",
        price=35000,
        category="Desk Essentials",
        stock=80,
    ),
    Product(
        id="PROD009",
        name="Correction Pen",
        description="Fast-drying correction fluid in a convenient pen format. Works on all paper types.",
        price=6000,
        category="Desk Essentials",
        stock=200,
    ),
    Product(
        id="PROD010",
        name="Stainless Steel Scissors (8 inch)",
        description="Sharp, rust-resistant stainless steel scissors with comfortable soft-grip handles.",
        price=18000,
        category="Desk Essentials",
        stock=90,
    ),
    Product(
        id="PROD011",
        name="Transparent 30cm Ruler",
        description="Break-resistant transparent ruler with metric and imperial markings.",
        price=4500,
        category="Geometry",
        stock=350,
    ),
    Product(
        id="PROD012",
        name="Geometry Box (7-piece set)",
        description="Includes compass, divider, set squares (45° & 60°), protractor, ruler, and pencil.",
        price=14900,
        category="Geometry",
        stock=110,
    ),
]


async def seed() -> None:
    """Insert all products into the database, skipping ones that already exist."""
    async with async_session_maker() as session:
        for product in PRODUCTS:
            await session.merge(product)
        await session.commit()
    print(f"Seeded {len(PRODUCTS)} products.")


if __name__ == "__main__":
    asyncio.run(seed())
