from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import get_current_user, require_admin
from app.db.database import get_db
from app.db.models import Product, User
from app.models.schema import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


async def fetch_all_products(db: AsyncSession) -> List[Product]:
    """Return all products sorted by category then name."""
    result = await db.execute(select(Product).order_by(Product.category, Product.name))
    return result.scalars().all()


async def fetch_product_by_id(product_id: str, db: AsyncSession) -> Optional[Product]:
    """Return a single product by ID, or None if not found."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def generate_product_id(db: AsyncSession) -> str:
    """Generate the next sequential product ID in the format PROD001."""
    result = await db.execute(select(func.count()).select_from(Product))
    count = result.scalar_one()
    return f"PROD{count + 1:03d}"


async def insert_product(data: ProductCreate, db: AsyncSession) -> Product:
    """Persist a new product to the catalog and return the saved record."""
    product = Product(
        id=await generate_product_id(db),
        name=data.name,
        description=data.description,
        price=data.price,
        category=data.category,
        stock=data.stock,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/", response_model=List[ProductResponse], status_code=200)
async def get_all_products(
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the full product catalog — available to all authenticated users."""
    return await fetch_all_products(db)


@router.get("/{product_id}", response_model=ProductResponse, status_code=200)
async def get_product(
    product_id: str,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return a single product by ID."""
    product = await fetch_product_by_id(product_id, db)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find product {product_id}. It may no longer be available.",
        )
    return product


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Add a new product to the catalog — admin only."""
    return await insert_product(data, db)
