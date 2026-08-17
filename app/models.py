from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class PermissionCode:
    PRODUCT_MANAGE_OWN = "product.manage_own"
    PRODUCT_REVIEW = "product.review"
    USER_MANAGE = "user.manage"
    ADMIN_ACCESS = "admin.access"
    ORDER_CREATE = "order.create"
    ORDER_REVIEW = "order.review"


class ProductStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class OrderStatus:
    CREATED = "created"
    CONFIRMED = "confirmed"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class AccountMixin(UserMixin, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self) -> str:
        return f"{self.account_type}:{self.id}"


class AdminUser(AccountMixin, db.Model):
    __tablename__ = "admin_users"

    account_type = "admin"

    def has_permission(self, code: str) -> bool:
        if not self.is_active:
            return False
        return code in {
            PermissionCode.PRODUCT_REVIEW,
            PermissionCode.USER_MANAGE,
            PermissionCode.ADMIN_ACCESS,
            PermissionCode.ORDER_REVIEW,
        }

    @property
    def is_admin(self) -> bool:
        return True

    @property
    def is_retailer(self) -> bool:
        return False

    @property
    def primary_role_label(self) -> str:
        return "Administrator"

    def __repr__(self) -> str:
        return f"<AdminUser {self.username}>"


class RegisteredUser(AccountMixin, db.Model):
    __tablename__ = "registered_users"

    account_type = "registered"

    is_retailer = db.Column(db.Boolean, nullable=False, default=False)
    products = db.relationship("Product", back_populates="seller", lazy=True)
    cart_items = db.relationship(
        "CartItem",
        back_populates="buyer",
        cascade="all, delete-orphan",
        lazy=True,
        foreign_keys="CartItem.buyer_id",
    )
    orders = db.relationship(
        "Order",
        back_populates="buyer",
        cascade="all, delete-orphan",
        lazy=True,
        foreign_keys="Order.buyer_id",
    )
    sold_order_items = db.relationship(
        "OrderItem",
        back_populates="seller",
        lazy=True,
        foreign_keys="OrderItem.seller_id",
    )

    def has_permission(self, code: str) -> bool:
        if not self.is_active:
            return False
        return code in {
            PermissionCode.PRODUCT_MANAGE_OWN,
            PermissionCode.ORDER_CREATE,
        }

    @property
    def is_admin(self) -> bool:
        return False

    @property
    def primary_role_label(self) -> str:
        return "Retailer" if self.is_retailer else "Registered User"

    def __repr__(self) -> str:
        return f"<RegisteredUser {self.username}>"


class Category(TimestampMixin, db.Model):
    __tablename__ = "music_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)

    products = db.relationship("Product", back_populates="category", lazy=True)

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Product(TimestampMixin, db.Model):
    __tablename__ = "music_listings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, index=True)
    artist = db.Column(db.String(120), nullable=False, index=True)
    format_type = db.Column(db.String(32), nullable=False, default="album")
    description = db.Column(db.Text, nullable=False)
    release_date = db.Column(db.Date)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    stock = db.Column(db.Integer, nullable=False, default=1)
    image_url = db.Column(db.String(255))
    approval_status = db.Column(db.String(16), nullable=False, default=ProductStatus.PENDING, index=True)

    seller_id = db.Column(db.Integer, db.ForeignKey("registered_users.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("music_categories.id"), nullable=False, index=True)

    seller = db.relationship("RegisteredUser", back_populates="products")
    category = db.relationship("Category", back_populates="products")
    cart_items = db.relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True,
    )
    order_items = db.relationship("OrderItem", back_populates="product", lazy=True)

    @property
    def is_public(self) -> bool:
        return self.approval_status == ProductStatus.APPROVED

    @property
    def format_label(self) -> str:
        mapping = {"album": "Album", "single": "Single", "ep": "EP"}
        return mapping.get(self.format_type, self.format_type.title())

    def __repr__(self) -> str:
        return f"<Product {self.title}>"


class CartItem(TimestampMixin, db.Model):
    __tablename__ = "shopping_cart_items"
    __table_args__ = (
        db.UniqueConstraint("buyer_id", "product_id", name="uq_shopping_cart_item_buyer_product"),
    )

    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("registered_users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("music_listings.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    buyer = db.relationship("RegisteredUser", back_populates="cart_items", foreign_keys=[buyer_id])
    product = db.relationship("Product", back_populates="cart_items")

    @property
    def line_total(self) -> Decimal:
        return Decimal(self.product.price) * self.quantity

    def __repr__(self) -> str:
        return f"<CartItem buyer={self.buyer_id} product={self.product_id}>"


class Order(TimestampMixin, db.Model):
    __tablename__ = "customer_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(24), unique=True, nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("registered_users.id"), nullable=False, index=True)
    status = db.Column(db.String(16), nullable=False, default=OrderStatus.CREATED, index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    buyer = db.relationship("RegisteredUser", back_populates="orders", foreign_keys=[buyer_id])
    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="OrderItem.id.asc()",
    )

    @property
    def status_label(self) -> str:
        labels = {
            OrderStatus.CREATED: "Created",
            OrderStatus.CONFIRMED: "Confirmed",
            OrderStatus.FULFILLED: "Fulfilled",
            OrderStatus.CANCELLED: "Cancelled",
        }
        return labels.get(self.status, self.status.title())

    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items)

    def __repr__(self) -> str:
        return f"<Order {self.order_number}>"


class OrderItem(TimestampMixin, db.Model):
    __tablename__ = "customer_order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("customer_orders.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("music_listings.id"), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("registered_users.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")
    seller = db.relationship("RegisteredUser", back_populates="sold_order_items", foreign_keys=[seller_id])

    @property
    def line_total(self) -> Decimal:
        return Decimal(self.unit_price) * self.quantity

    def __repr__(self) -> str:
        return f"<OrderItem order={self.order_id} product={self.product_id}>"
