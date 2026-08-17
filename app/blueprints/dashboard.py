from __future__ import annotations

from decimal import Decimal

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc, func

from app.decorators import permission_required
from app.extensions import db
from app.forms import ProductForm
from app.models import AdminUser, Category, Order, PermissionCode, Product, ProductStatus, RegisteredUser


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def populate_product_form_choices(form: ProductForm) -> None:
    categories = db.session.scalars(db.select(Category).order_by(Category.name.asc())).all()
    form.category_id.choices = [(category.id, category.name) for category in categories]


def user_can_edit_product(product: Product) -> bool:
    return (
        current_user.is_authenticated
        and current_user.has_permission(PermissionCode.PRODUCT_MANAGE_OWN)
        and product.seller_id == current_user.id
    )


# >>> API ENTRY: GET /dashboard/ - user/admin dashboard home <<<
@dashboard_bp.get("/")
@login_required
def home():
    if current_user.is_admin:
        stats = {
            "admin_accounts": db.session.scalar(db.select(func.count()).select_from(AdminUser)) or 0,
            "registered_users": db.session.scalar(db.select(func.count()).select_from(RegisteredUser)) or 0,
            "music_listings": db.session.scalar(db.select(func.count()).select_from(Product)) or 0,
            "orders": db.session.scalar(db.select(func.count()).select_from(Order)) or 0,
            "pending_review": db.session.scalar(
                db.select(func.count()).select_from(
                    db.select(Product.id).where(Product.approval_status == ProductStatus.PENDING).subquery()
                )
            )
            or 0,
        }
        recent_products = db.session.scalars(
            db.select(Product).order_by(Product.created_at.desc()).limit(5)
        ).all()
        recent_users = db.session.scalars(
            db.select(RegisteredUser).order_by(RegisteredUser.created_at.desc()).limit(5)
        ).all()
        return render_template(
            "dashboard/index.html",
            stats=stats,
            recent_products=recent_products,
            recent_users=recent_users,
        )

    stats = {
        "my_listings": db.session.scalar(
            db.select(func.count()).select_from(
                db.select(Product.id).where(Product.seller_id == current_user.id).subquery()
            )
        )
        or 0,
        "my_orders": db.session.scalar(
            db.select(func.count()).select_from(
                db.select(Order.id).where(Order.buyer_id == current_user.id).subquery()
            )
        )
        or 0,
        "approved": db.session.scalar(
            db.select(func.count()).select_from(
                db.select(Product.id)
                .where(
                    Product.seller_id == current_user.id,
                    Product.approval_status == ProductStatus.APPROVED,
                )
                .subquery()
            )
        )
        or 0,
        "pending_review": db.session.scalar(
            db.select(func.count()).select_from(
                db.select(Product.id)
                .where(
                    Product.seller_id == current_user.id,
                    Product.approval_status == ProductStatus.PENDING,
                )
                .subquery()
            )
        )
        or 0,
        "rejected": db.session.scalar(
            db.select(func.count()).select_from(
                db.select(Product.id)
                .where(
                    Product.seller_id == current_user.id,
                    Product.approval_status == ProductStatus.REJECTED,
                )
                .subquery()
            )
        )
        or 0,
    }
    recent_products = db.session.scalars(
        db.select(Product)
        .where(Product.seller_id == current_user.id)
        .order_by(Product.created_at.desc())
        .limit(5)
    ).all()
    recent_public_products = db.session.scalars(
        db.select(Product)
        .where(Product.approval_status == ProductStatus.APPROVED)
        .order_by(Product.created_at.desc())
        .limit(5)
    ).all()

    return render_template(
        "dashboard/index.html",
        stats=stats,
        recent_products=recent_products,
        recent_public_products=recent_public_products,
    )


# >>> API ENTRY: GET /dashboard/products - user's product listings <<<
@dashboard_bp.get("/products")
@permission_required(PermissionCode.PRODUCT_MANAGE_OWN)
def products():
    products_list = db.session.scalars(
        db.select(Product)
        .where(Product.seller_id == current_user.id)
        .order_by(desc(Product.created_at))
    ).all()
    return render_template("dashboard/products.html", products=products_list)


# >>> API ENTRY: GET/POST /dashboard/products/create - create product listing <<<
@dashboard_bp.route("/products/create", methods=["GET", "POST"])
@permission_required(PermissionCode.PRODUCT_MANAGE_OWN)
def product_create():
    form = ProductForm()
    populate_product_form_choices(form)

    if form.validate_on_submit():
        product = Product(
            title=form.title.data.strip(),
            artist=form.artist.data.strip(),
            format_type=form.format_type.data,
            category_id=form.category_id.data,
            release_date=form.release_date.data,
            price=Decimal(form.price.data),
            stock=form.stock.data,
            image_url=form.image_url.data.strip() if form.image_url.data else None,
            description=form.description.data.strip(),
            seller=current_user,
            approval_status=ProductStatus.PENDING,
        )
        db.session.add(product)
        db.session.commit()
        flash("Listing created and sent for administrator review.", "success")
        return redirect(url_for("dashboard.products"))

    return render_template(
        "dashboard/product_form.html",
        form=form,
        page_title="New Listing",
        product=None,
    )


# >>> API ENTRY: GET/POST /dashboard/products/<product_id>/edit - edit product listing <<<
@dashboard_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@permission_required(PermissionCode.PRODUCT_MANAGE_OWN)
def product_edit(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)
    if not user_can_edit_product(product):
        abort(403)

    form = ProductForm(obj=product)
    populate_product_form_choices(form)

    if form.validate_on_submit():
        form.populate_obj(product)
        product.image_url = form.image_url.data.strip() if form.image_url.data else None
        product.description = form.description.data.strip()
        product.approval_status = ProductStatus.PENDING
        db.session.commit()
        flash("Listing updated and returned to pending review.", "success")
        return redirect(url_for("dashboard.products"))

    return render_template(
        "dashboard/product_form.html",
        form=form,
        page_title="Edit Listing",
        product=product,
    )


# >>> API ENTRY: POST /dashboard/products/<product_id>/delete - delete product listing <<<
@dashboard_bp.post("/products/<int:product_id>/delete")
@permission_required(PermissionCode.PRODUCT_MANAGE_OWN)
def product_delete(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)
    if not user_can_edit_product(product):
        abort(403)
    if product.order_items:
        flash("This listing is already linked to an order and cannot be deleted.", "error")
        return redirect(url_for("dashboard.products"))

    for cart_item in list(product.cart_items):
        db.session.delete(cart_item)

    db.session.delete(product)
    db.session.commit()
    flash("Listing removed.", "info")
    return redirect(url_for("dashboard.products"))


# >>> API ENTRY: GET /dashboard/admin/users - admin user management <<<
@dashboard_bp.get("/admin/users")
@permission_required(PermissionCode.USER_MANAGE)
def admin_users():
    admins = db.session.scalars(db.select(AdminUser).order_by(AdminUser.created_at.asc())).all()
    users = db.session.scalars(db.select(RegisteredUser).order_by(RegisteredUser.created_at.desc())).all()
    return render_template("dashboard/admin_users.html", admins=admins, users=users)


# >>> API ENTRY: POST /dashboard/admin/users/<user_id>/toggle-active - enable/disable user <<<
@dashboard_bp.post("/admin/users/<int:user_id>/toggle-active")
@permission_required(PermissionCode.USER_MANAGE)
def admin_user_toggle_active(user_id: int):
    user = db.session.get(RegisteredUser, user_id)
    if user is None:
        abort(404)

    user.is_active = not user.is_active
    db.session.commit()
    flash(f"{user.display_name} has been updated.", "success")
    return redirect(url_for("dashboard.admin_users"))


# >>> API ENTRY: GET /dashboard/admin/products - admin product review list <<<
@dashboard_bp.get("/admin/products")
@permission_required(PermissionCode.PRODUCT_REVIEW)
def admin_products():
    products_list = db.session.scalars(
        db.select(Product).order_by(desc(Product.created_at))
    ).all()
    return render_template("dashboard/admin_products.html", products=products_list)


# >>> API ENTRY: POST /dashboard/admin/products/<product_id>/review - review product listing <<<
@dashboard_bp.post("/admin/products/<int:product_id>/review")
@permission_required(PermissionCode.PRODUCT_REVIEW)
def admin_product_review(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)

    approval_status = request.form.get("approval_status", ProductStatus.PENDING)
    if approval_status not in {ProductStatus.PENDING, ProductStatus.APPROVED, ProductStatus.REJECTED}:
        flash("Unsupported review status.", "error")
        return redirect(url_for("dashboard.admin_products"))

    product.approval_status = approval_status
    db.session.commit()
    flash(f"{product.title} updated.", "success")
    return redirect(url_for("dashboard.admin_products"))
