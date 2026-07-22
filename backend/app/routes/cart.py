from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import require_customer
from app.db.database import get_db
from app.db.models import CartItem, Order, Product, User
from app.models.schema import AddToCartRequest, CartItemResponse, CartResponse, OrderResponse

router = APIRouter(prefix="/cart", tags=["cart"])


def _build_cart_item(cart_item: CartItem, product: Product) -> CartItemResponse:
    """Build a CartItemResponse from a cart item row and its associated product."""
    return CartItemResponse(
        id=cart_item.id,
        product_id=product.id,
        product_name=product.name,
        quantity=cart_item.quantity,
        unit_price=product.price,
        subtotal=product.price * cart_item.quantity,
    )


async def fetch_cart_items(user_id: int, db: AsyncSession) -> List[CartItemResponse]:
    """Return all cart items with product details for the given user."""
    result = await db.execute(
        select(CartItem, Product)
        .join(Product, CartItem.product_id == Product.id)
        .where(CartItem.user_id == user_id)
    )
    return [_build_cart_item(ci, p) for ci, p in result.all()]


async def fetch_cart_row(user_id: int, product_id: str, db: AsyncSession):
    """Return the CartItem row for a user/product pair, or None."""
    result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
        )
    )
    return result.scalar_one_or_none()


async def upsert_cart_item(user_id: int, product_id: str, quantity: int, db: AsyncSession) -> CartItem:
    """Increment quantity on an existing cart row, or create a new one."""
    existing = await fetch_cart_row(user_id, product_id, db)
    if existing:
        existing.quantity += quantity
        await db.commit()
        await db.refresh(existing)
        return existing
    item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def validate_stock(items: List[CartItemResponse], db: AsyncSession) -> None:
    """Raise 400 if any item in the cart has insufficient stock at checkout time."""
    for item in items:
        product = await db.get(Product, item.product_id)
        if product is None or product.stock < item.quantity:
            name = product.name if product else item.product_name
            raise HTTPException(
                status_code=400,
                detail=f"Sorry, {name} doesn't have enough stock for your order. Please update your cart.",
            )


async def reduce_stock(items: List[CartItemResponse], db: AsyncSession) -> None:
    """Decrease product stock for each cart item after a successful checkout."""
    for item in items:
        product = await db.get(Product, item.product_id)
        if product:
            product.stock -= item.quantity
    await db.commit()


async def generate_order_id(db: AsyncSession) -> str:
    """Generate the next sequential order ID in the format ORD001."""
    result = await db.execute(select(func.count()).select_from(Order))
    count = result.scalar_one()
    return f"ORD{count + 1:03d}"


async def create_order_from_cart(user: User, items: List[CartItemResponse], db: AsyncSession) -> Order:
    """Create and persist an Order from the user's cart contents."""
    order = Order(
        id=await generate_order_id(db),
        user_id=user.id,
        customer=user.email,
        items=[f"{i.product_name} x{i.quantity}" for i in items],
        status="pending",
        total=sum(i.subtotal for i in items),
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def clear_cart(user_id: int, db: AsyncSession) -> None:
    """Delete all cart items for the given user."""
    await db.execute(delete(CartItem).where(CartItem.user_id == user_id))
    await db.commit()


@router.get("/", response_model=CartResponse, status_code=200)
async def get_cart(current_user: User = Depends(require_customer), db: AsyncSession = Depends(get_db)):
    """Return the current customer's cart with product details and running total."""
    items = await fetch_cart_items(current_user.id, db)
    return CartResponse(items=items, total=sum(i.subtotal for i in items))


@router.post("/items/", response_model=CartItemResponse, status_code=201)
async def add_to_cart(
    data: AddToCartRequest,
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db),
):
    """Add a product to the cart — increments quantity if already present."""
    product = await db.get(Product, data.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="We couldn't find that product. It may no longer be available.")
    existing = await fetch_cart_row(current_user.id, data.product_id, db)
    already_in_cart = existing.quantity if existing else 0
    if product.stock < already_in_cart + data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock - already_in_cart} more unit(s) of {product.name} can be added.",
        )
    cart_item = await upsert_cart_item(current_user.id, data.product_id, data.quantity, db)
    return _build_cart_item(cart_item, product)


@router.delete("/items/{product_id}", status_code=204)
async def remove_from_cart(
    product_id: str,
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db),
):
    """Remove a product from the cart entirely."""
    item = await fetch_cart_row(current_user.id, product_id, db)
    if item is None:
        raise HTTPException(status_code=404, detail="That item isn't in your cart.")
    await db.delete(item)
    await db.commit()


@router.post("/checkout/", response_model=OrderResponse, status_code=201)
async def checkout(current_user: User = Depends(require_customer), db: AsyncSession = Depends(get_db)):
    """Place an order from the cart, reduce stock, and clear the cart."""
    items = await fetch_cart_items(current_user.id, db)
    if not items:
        raise HTTPException(status_code=400, detail="Your cart is empty. Add some items before checking out!")
    await validate_stock(items, db)
    order = await create_order_from_cart(current_user, items, db)
    await reduce_stock(items, db)
    await clear_cart(current_user.id, db)
    return order
