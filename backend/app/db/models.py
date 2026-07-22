from sqlalchemy import Boolean, Column, String, Integer, TIMESTAMP, ARRAY, Text, Date, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql import func
from app.db.database import Base


class Product(Base):
    """SQLAlchemy model for the products table."""

    __tablename__ = "products"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    stock = Column(Integer, nullable=False, server_default="0")
    created_at = Column(TIMESTAMP, server_default=func.now())


class CartItem(Base):
    """SQLAlchemy model for the cart_items table."""

    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, server_default="1")
    created_at = Column(TIMESTAMP, server_default=func.now())


class Notification(Base):
    """SQLAlchemy model for the notifications table."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(TIMESTAMP, server_default=func.now())


class PasswordResetToken(Base):
    """SQLAlchemy model for the password_reset_tokens table."""

    __tablename__ = "password_reset_tokens"

    token = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    used = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(TIMESTAMP, server_default=func.now())


class User(Base):
    """SQLAlchemy model for the users table."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, server_default="customer")


class Order(Base):
    """SQLAlchemy model for the orders table."""

    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer = Column(String, nullable=False)
    items = Column(ARRAY(Text), nullable=False)
    status = Column(String, nullable=False)
    total = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Ticket(Base):
    """SQLAlchemy model for the tickets table."""

    __tablename__ = "tickets"

    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    issue = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Tracking(Base):
    """SQLAlchemy model for the tracking table."""

    __tablename__ = "tracking"

    order_id = Column(String, ForeignKey("orders.id"), primary_key=True)
    location = Column(String, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now())
    eta = Column(Date, nullable=True)
