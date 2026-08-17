from __future__ import annotations

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import desc, func, or_

from app.extensions import db
from app.models import Category, PermissionCode, Product, ProductStatus


public_bp = Blueprint("public", __name__)


PROJECT_HIGHLIGHTS = [
    {
        "eyebrow": "Registration",
        "title": "New users can create registered user or retailer accounts.",
        "text": "Create an account, manage access securely, and return to saved marketplace activity whenever needed.",
    },
    {
        "eyebrow": "Search",
        "title": "Search vinyl by artist, album, single, or EP title.",
        "text": "Use keyword search, format filters, and detailed record pages to find the right release quickly.",
    },
    {
        "eyebrow": "Moderation",
        "title": "Administrators monitor submitted record listings.",
        "text": "New and updated listings are reviewed before they appear publicly, keeping catalog quality consistent.",
    },
    {
        "eyebrow": "Bag",
        "title": "Add vinyl to a bag and submit an order request.",
        "text": "Orders keep quantity, price, and status details together so buyers and administrators can track activity clearly.",
    },
]


PLACEHOLDER_ADS = [
    {
        "badge": "Featured",
        "eyebrow": "Retailer Spotlight",
        "title": "Independent shops and curated crates.",
        "text": "Explore selected vinyl from trusted registered users and discover records that fit your collection.",
        "link_label": "Browse Vinyl",
        "endpoint": "public.catalog",
        "tone": 0,
    },
    {
        "badge": "Local Scene",
        "eyebrow": "Music Event",
        "title": "Record fairs, listening nights, and community finds.",
        "text": "Create an account to follow new listings and keep track of records you want to order.",
        "link_label": "Create Account",
        "endpoint": "auth.register",
        "tone": 1,
    },
    {
        "badge": "Collector Pick",
        "eyebrow": "Collector Tools",
        "title": "Sleeves, care tools, and essentials for collectors.",
        "text": "Browse records by format, category, artist, and release details from one focused catalog.",
        "link_label": "Open Search",
        "endpoint": "public.catalog",
        "tone": 2,
    },
]


def public_product_statement():
    return db.select(Product).where(Product.approval_status == ProductStatus.APPROVED)


# >>> API ENTRY: GET / - public home page <<<
@public_bp.get("/")
def home():
    highlighted_products = db.session.scalars(
        public_product_statement().order_by(Product.created_at.desc()).limit(6)
    ).all()

    latest_products = db.session.scalars(
        public_product_statement().order_by(Product.created_at.desc()).limit(9)
    ).all()

    spotlight_product = highlighted_products[0] if highlighted_products else None

    total_products = db.session.scalar(
        db.select(func.count()).select_from(public_product_statement().subquery())
    ) or 0
    seller_count = db.session.scalar(
        db.select(func.count(func.distinct(Product.seller_id))).where(
            Product.approval_status == ProductStatus.APPROVED,
        )
    ) or 0
    category_count = db.session.scalar(db.select(func.count()).select_from(Category)) or 0

    return render_template(
        "home.html",
        highlighted_products=highlighted_products,
        latest_products=latest_products,
        spotlight_product=spotlight_product,
        total_products=total_products,
        seller_count=seller_count,
        category_count=category_count,
        project_highlights=PROJECT_HIGHLIGHTS,
        placeholder_ads=PLACEHOLDER_ADS,
    )


# >>> API ENTRY: GET /catalog - catalog search/filter page <<<
@public_bp.get("/catalog")
def catalog():
    search = request.args.get("q", "").strip()
    format_type = request.args.get("format", "all").strip().lower()
    sort = request.args.get("sort", "newest").strip().lower()
    category_slug = request.args.get("category", "").strip().lower()
    page = request.args.get("page", default=1, type=int)

    stmt = public_product_statement()

    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                Product.title.ilike(like),
                Product.artist.ilike(like),
            )
        )

    if format_type in {"album", "single", "ep"}:
        stmt = stmt.where(Product.format_type == format_type)

    if category_slug:
        stmt = stmt.join(Product.category).where(Category.slug == category_slug)

    if sort == "price-asc":
        stmt = stmt.order_by(Product.price.asc(), Product.created_at.desc())
    elif sort == "price-desc":
        stmt = stmt.order_by(Product.price.desc(), Product.created_at.desc())
    else:
        stmt = stmt.order_by(Product.created_at.desc())

    products = db.paginate(
        stmt,
        page=page,
        per_page=current_app.config["PRODUCTS_PER_PAGE"],
        error_out=False,
    )
    categories = db.session.scalars(db.select(Category).order_by(Category.name.asc())).all()

    return render_template(
        "catalog/list.html",
        products=products,
        categories=categories,
        filters={
            "q": search,
            "format": format_type,
            "sort": sort,
            "category": category_slug,
        },
    )


# >>> API ENTRY: GET /products/<product_id> - product detail page <<<
@public_bp.get("/products/<int:product_id>")
def product_detail(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)

    is_owner = (
        current_user.is_authenticated
        and not current_user.is_admin
        and current_user.id == product.seller_id
    )
    is_admin = current_user.is_authenticated and current_user.has_permission(PermissionCode.ADMIN_ACCESS)
    if not product.is_public and not (is_owner or is_admin):
        abort(404)

    related_products = db.session.scalars(
        public_product_statement()
        .where(Product.id != product.id, Product.category_id == product.category_id)
        .order_by(desc(Product.created_at))
        .limit(3)
    ).all()

    return render_template(
        "catalog/detail.html",
        product=product,
        related_products=related_products,
    )


# >>> API ENTRY: GET /search-snapshot - catalog summary JSON <<<
@public_bp.get("/search-snapshot")
def search_snapshot():
    total_products = db.session.scalar(
        db.select(func.count()).select_from(
            db.select(Product.id)
            .where(Product.approval_status == ProductStatus.APPROVED)
            .subquery()
        )
    )
    return {
        "totalProducts": total_products,
        "formats": ["album", "single", "ep"],
    }


# >>> API ENTRY: GET /favicon.ico - browser favicon fallback <<<
@public_bp.get("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.svg"), code=301)
