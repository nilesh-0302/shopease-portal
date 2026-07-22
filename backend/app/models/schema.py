from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel


class ForgotPasswordRequest(BaseModel):
    """Pydantic schema for requesting a password reset."""

    email: str


class ForgotPasswordResponse(BaseModel):
    """Pydantic schema for the forgot-password response containing the reset token."""

    reset_token: str
    expires_at: datetime


class ResetPasswordRequest(BaseModel):
    """Pydantic schema for resetting a password using a token."""

    token: str
    new_password: str


class UserCreate(BaseModel):
    """Pydantic schema for registering a new user."""

    email: str
    password: str
    name: Optional[str] = None


class CustomerProfileResponse(BaseModel):
    """Pydantic schema for a customer's own profile."""

    id: int
    email: str
    name: Optional[str]
    role: str

    model_config = {"from_attributes": True}


class PromoteRequest(BaseModel):
    """Pydantic schema for promoting or demoting a user's role."""

    email: str
    role: Literal["admin", "customer"]


class UserResponse(BaseModel):
    """Pydantic schema for a user record returned by the API."""

    id: int
    email: str
    role: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Pydantic schema for the JWT token response."""

    access_token: str
    token_type: str = "bearer"


class OrderCreate(BaseModel):
    """Pydantic schema for creating a new order."""

    customer: str
    items: List[str]
    status: str
    total: int


class OrderResponse(BaseModel):
    """Pydantic schema for a single order returned by the API."""

    id: str
    customer: str
    items: List[str]
    status: str
    total: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketCreate(BaseModel):
    """Pydantic schema for creating a new support ticket."""

    order_id: str
    issue: str


class TicketResponse(BaseModel):
    """Pydantic schema for a support ticket returned by the API."""

    id: str
    order_id: str
    issue: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TrackingCreate(BaseModel):
    """Pydantic schema for adding tracking info to an order."""

    order_id: str
    location: str
    eta: Optional[date] = None


class NotificationResponse(BaseModel):
    """Pydantic schema for a notification returned by the API."""

    id: int
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    """Pydantic schema for creating a new product."""

    name: str
    description: Optional[str] = None
    price: int
    category: str
    stock: int


class ProductResponse(BaseModel):
    """Pydantic schema for a product returned by the API."""

    id: str
    name: str
    description: Optional[str]
    price: int
    category: str
    stock: int

    model_config = {"from_attributes": True}


class AddToCartRequest(BaseModel):
    """Pydantic schema for adding a product to the cart."""

    product_id: str
    quantity: int = 1


class CartItemResponse(BaseModel):
    """Pydantic schema for a single cart item with product details and subtotal."""

    id: int
    product_id: str
    product_name: str
    quantity: int
    unit_price: int
    subtotal: int


class CartResponse(BaseModel):
    """Pydantic schema for the full cart with items and running total."""

    items: List[CartItemResponse]
    total: int


class TrackingResponse(BaseModel):
    """Pydantic schema for order tracking info returned by the API."""

    order_id: str
    location: str
    updated_at: datetime
    eta: Optional[date]

    model_config = {"from_attributes": True}
