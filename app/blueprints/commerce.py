from __future__ import annotations

from decimal import Decimal

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc

from app.decorators import permission_required
from app.extensions import db
from app.models import CartItem, Order, OrderItem, OrderStatus, PermissionCode, Product
from app.utils import generate_order_number


commerce_bp = Blueprint("commerce", __name__)


ORDER_STATUS_OPTIONS = [
    OrderStatus.CREATED,
    OrderStatus.CONFIRMED,
    OrderStatus.FULFILLED,
    OrderStatus.CANCELLED,
]


def requested_quantity() -> int | None:
    try:
        quantity = int(request.form.get("quantity", "1"))
    except (TypeError, ValueError):
        return None
    if quantity < 1 or quantity > 99:
        return None
    return quantity


def order_number_candidate() -> str:
    while True:
        candidate = generate_order_number()
        existing = db.session.scalar(db.select(Order.id).where(Order.order_number == candidate))
        if existing is None:
            return candidate


def bag_items_for_current_user() -> list[CartItem]:
    return db.session.scalars(
        db.select(CartItem)
        .where(CartItem.buyer_id == current_user.id)
        .order_by(desc(CartItem.created_at))
    ).all()


def bag_subtotal(items: list[CartItem]) -> Decimal:
    return sum((item.line_total for item in items), start=Decimal("0.00"))


def buyable_product_or_404(product_id: int) -> Product:
    product = db.session.get(Product, product_id)
    if product is None or not product.is_public:
        abort(404)
    return product


def ensure_product_can_be_ordered(product: Product, quantity: int) -> str | None:
    if product.seller_id == current_user.id:
        return "You cannot order your own listing."
    if product.stock <= 0:
        return "This listing is currently sold out."
    if quantity > product.stock:
        return f"Only {product.stock} copies are available right now."
    return None


def create_order_from_entries(
    *,
    buyer_id: int,
    entries: list[dict[str, int]],
    source_cart_items: list[CartItem] | None = None,
) -> Order:
    if not entries:
        raise ValueError("Your bag is empty.")

    product_ids = sorted({entry["product_id"] for entry in entries})
    locked_products = {
        product.id: product
        for product in db.session.scalars(
            db.select(Product).where(Product.id.in_(product_ids)).with_for_update()
        ).all()
    }

    order = Order(
        order_number=order_number_candidate(),
        buyer_id=buyer_id,
        status=OrderStatus.CREATED,
        total_amount=Decimal("0.00"),
    )
    db.session.add(order)

    total_amount = Decimal("0.00")
    for entry in entries:
        product = locked_products.get(entry["product_id"])
        quantity = int(entry["quantity"])
        if product is None or not product.is_public:
            raise ValueError("One of the selected listings is no longer available.")
        if product.seller_id == buyer_id:
            raise ValueError("You cannot order your own listing.")
        if quantity < 1:
            raise ValueError("Order quantity must be at least 1.")
        if product.stock < quantity:
            raise ValueError(f"Only {product.stock} copies remain for {product.title}.")

        product.stock -= quantity
        order_item = OrderItem(
            order=order,
            product=product,
            seller_id=product.seller_id,
            quantity=quantity,
            unit_price=Decimal(product.price),
        )
        db.session.add(order_item)
        total_amount += order_item.line_total

    order.total_amount = total_amount

    for cart_item in source_cart_items or []:
        db.session.delete(cart_item)

    db.session.commit()
    return order


def order_for_viewer_or_404(order_id: int) -> Order:
    order = db.session.get(Order, order_id)
    if order is None:
        abort(404)
    if current_user.is_admin:
        return order
    if not current_user.is_authenticated or order.buyer_id != current_user.id:
        abort(404)
    return order


# >>> API ENTRY: POST /products/<product_id>/bag - add product to bag <<<
@commerce_bp.post("/products/<int:product_id>/bag")
@permission_required(PermissionCode.ORDER_CREATE)
def add_to_bag(product_id: int):
    product = buyable_product_or_404(product_id)
    quantity = requested_quantity()
    if quantity is None:
        flash("Please choose a quantity between 1 and 99.", "error")
        return redirect(url_for("public.product_detail", product_id=product.id))

    error = ensure_product_can_be_ordered(product, quantity)
    if error:
        flash(error, "error")
        return redirect(url_for("public.product_detail", product_id=product.id))

    item = db.session.scalar(
        db.select(CartItem).where(
            CartItem.buyer_id == current_user.id,
            CartItem.product_id == product.id,
        )
    )
    if item is None:
        item = CartItem(buyer_id=current_user.id, product_id=product.id, quantity=quantity)
        db.session.add(item)
    else:
        merged_quantity = item.quantity + quantity
        if merged_quantity > product.stock:
            flash(f"Your bag already contains this listing. The maximum available is {product.stock}.", "error")
            return redirect(url_for("commerce.bag"))
        item.quantity = merged_quantity

    db.session.commit()
    flash("Added to bag.", "success")
    return redirect(url_for("commerce.bag"))


# >>> API ENTRY: POST /products/<product_id>/buy-now - create direct order <<<
@commerce_bp.post("/products/<int:product_id>/buy-now")
@permission_required(PermissionCode.ORDER_CREATE)
def buy_now(product_id: int):
    product = buyable_product_or_404(product_id)
    quantity = requested_quantity()
    if quantity is None:
        flash("Please choose a quantity between 1 and 99.", "error")
        return redirect(url_for("public.product_detail", product_id=product.id))

    error = ensure_product_can_be_ordered(product, quantity)
    if error:
        flash(error, "error")
        return redirect(url_for("public.product_detail", product_id=product.id))

    try:
        order = create_order_from_entries(
            buyer_id=current_user.id,
            entries=[{"product_id": product.id, "quantity": quantity}],
        )
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "error")
        return redirect(url_for("public.product_detail", product_id=product.id))

    flash(f"Order {order.order_number} created.", "success")
    return redirect(url_for("commerce.order_detail", order_id=order.id))


# >>> API ENTRY: GET /bag - view shopping bag <<<
@commerce_bp.get("/bag")
@permission_required(PermissionCode.ORDER_CREATE)
def bag():
    items = bag_items_for_current_user()
    subtotal = bag_subtotal(items)
    return render_template(
        "store/bag.html",
        items=items,
        subtotal=subtotal,
        item_count=sum(item.quantity for item in items),
    )


# >>> API ENTRY: POST /bag/items/<item_id>/update - update bag item quantity <<<
@commerce_bp.post("/bag/items/<int:item_id>/update")
@permission_required(PermissionCode.ORDER_CREATE)
def bag_item_update(item_id: int):
    item = db.session.get(CartItem, item_id)
    if item is None or item.buyer_id != current_user.id:
        abort(404)

    quantity = requested_quantity()
    if quantity is None:
        flash("Please choose a quantity between 1 and 99.", "error")
        return redirect(url_for("commerce.bag"))
    if quantity > item.product.stock:
        flash(f"Only {item.product.stock} copies are available for this listing.", "error")
        return redirect(url_for("commerce.bag"))

    item.quantity = quantity
    db.session.commit()
    flash("Bag updated.", "success")
    return redirect(url_for("commerce.bag"))


# >>> API ENTRY: POST /bag/items/<item_id>/remove - remove bag item <<<
@commerce_bp.post("/bag/items/<int:item_id>/remove")
@permission_required(PermissionCode.ORDER_CREATE)
def bag_item_remove(item_id: int):
    item = db.session.get(CartItem, item_id)
    if item is None or item.buyer_id != current_user.id:
        abort(404)

    db.session.delete(item)
    db.session.commit()
    flash("Removed from bag.", "info")
    return redirect(url_for("commerce.bag"))


# >>> API ENTRY: POST /bag/checkout - create order from bag <<<
@commerce_bp.post("/bag/checkout")
@permission_required(PermissionCode.ORDER_CREATE)
def checkout():
    items = bag_items_for_current_user()
    try:
        order = create_order_from_entries(
            buyer_id=current_user.id,
            entries=[{"product_id": item.product_id, "quantity": item.quantity} for item in items],
            source_cart_items=items,
        )
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "error")
        return redirect(url_for("commerce.bag"))

    flash(f"Order {order.order_number} created from your bag.", "success")
    return redirect(url_for("commerce.order_detail", order_id=order.id))


# >>> API ENTRY: GET /orders - view buyer orders <<<
@commerce_bp.get("/orders")
@permission_required(PermissionCode.ORDER_CREATE)
def orders():
    orders_list = db.session.scalars(
        db.select(Order)
        .where(Order.buyer_id == current_user.id)
        .order_by(desc(Order.created_at))
    ).all()
    return render_template("store/orders.html", orders=orders_list)


# >>> API ENTRY: GET /orders/<order_id> - view order detail <<<
@commerce_bp.get("/orders/<int:order_id>")
@login_required
def order_detail(order_id: int):
    order = order_for_viewer_or_404(order_id)
    return render_template("store/order_detail.html", order=order)


# >>> API ENTRY: GET /dashboard/admin/orders - admin order list <<<
@commerce_bp.get("/dashboard/admin/orders")
@permission_required(PermissionCode.ORDER_REVIEW)
def admin_orders():
    orders_list = db.session.scalars(db.select(Order).order_by(desc(Order.created_at))).all()
    return render_template(
        "dashboard/admin_orders.html",
        orders=orders_list,
        status_options=ORDER_STATUS_OPTIONS,
    )


# >>> API ENTRY: POST /dashboard/admin/orders/<order_id>/status - update order status <<<
@commerce_bp.post("/dashboard/admin/orders/<int:order_id>/status")
@permission_required(PermissionCode.ORDER_REVIEW)
def admin_order_status(order_id: int):
    order = db.session.get(Order, order_id)
    if order is None:
        abort(404)

    status = request.form.get("status", OrderStatus.CREATED).strip().lower()
    if status not in ORDER_STATUS_OPTIONS:
        flash("Unsupported order status.", "error")
        return redirect(url_for("commerce.admin_orders"))

    order.status = status
    db.session.commit()
    flash(f"Order {order.order_number} updated.", "success")
    return redirect(url_for("commerce.admin_orders"))
