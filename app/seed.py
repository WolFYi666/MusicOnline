from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.account_policy import DEFAULT_ACCOUNT_PASSWORD
from app.extensions import db
from app.models import AdminUser, Category, Product, ProductStatus, RegisteredUser


CATEGORY_SPECS = [
    {
        "name": "Rock Classics",
        "slug": "rock-classics",
        "description": "Classic rock pressings, landmark albums, and essential guitar-led releases.",
    },
    {
        "name": "Pop Essentials",
        "slug": "pop-essentials",
        "description": "Pop albums, singles, and collector-friendly releases from defining artists.",
    },
    {
        "name": "Soul & R&B",
        "slug": "soul-rnb",
        "description": "Soul, R&B, and vocal records with rich arrangements and lasting appeal.",
    },
    {
        "name": "Electronic & Dance",
        "slug": "electronic-dance",
        "description": "Electronic, dance, and club-focused records for home listening or DJ shelves.",
    },
    {
        "name": "Jazz Corner",
        "slug": "jazz-corner",
        "description": "Jazz albums, reissues, and timeless recordings for focused collectors.",
    },
]


LISTING_SPECS = [
    {
        "title": "Rumours",
        "artist": "Fleetwood Mac",
        "format_type": "album",
        "category_slug": "rock-classics",
        "price": Decimal("188.00"),
        "stock": 6,
        "seller_key": "retailer",
        "status": ProductStatus.APPROVED,
        "release_date": date(1977, 2, 4),
        "description": "A classic album with warm harmonies, polished production, and enduring appeal for rock collectors.",
    },
    {
        "title": "The Dark Side of the Moon",
        "artist": "Pink Floyd",
        "format_type": "album",
        "category_slug": "rock-classics",
        "price": Decimal("216.00"),
        "stock": 5,
        "seller_key": "retailer",
        "status": ProductStatus.APPROVED,
        "release_date": date(1973, 3, 1),
        "description": "A landmark progressive rock album known for immersive production and a highly collectible vinyl presence.",
    },
    {
        "title": "Abbey Road",
        "artist": "The Beatles",
        "format_type": "album",
        "category_slug": "rock-classics",
        "price": Decimal("205.00"),
        "stock": 4,
        "seller_key": "registered_user",
        "status": ProductStatus.APPROVED,
        "release_date": date(1969, 9, 26),
        "description": "A beloved Beatles release with iconic songwriting, detailed arrangements, and lasting collector demand.",
    },
    {
        "title": "Chronic Town",
        "artist": "R.E.M.",
        "format_type": "ep",
        "category_slug": "rock-classics",
        "price": Decimal("118.00"),
        "stock": 9,
        "seller_key": "registered_user",
        "status": ProductStatus.APPROVED,
        "release_date": date(1982, 8, 24),
        "description": "An early R.E.M. EP with jangly guitars, compact sequencing, and strong alternative-rock character.",
    },
    {
        "title": "Thriller",
        "artist": "Michael Jackson",
        "format_type": "album",
        "category_slug": "pop-essentials",
        "price": Decimal("198.00"),
        "stock": 7,
        "seller_key": "retailer",
        "status": ProductStatus.APPROVED,
        "release_date": date(1982, 11, 30),
        "description": "A defining pop album packed with signature singles, crisp production, and wide collector interest.",
    },
    {
        "title": "1989",
        "artist": "Taylor Swift",
        "format_type": "album",
        "category_slug": "pop-essentials",
        "price": Decimal("176.00"),
        "stock": 9,
        "seller_key": "registered_user",
        "status": ProductStatus.APPROVED,
        "release_date": date(2014, 10, 27),
        "description": "A polished modern pop release with bright production, strong hooks, and broad audience appeal.",
    },
    {
        "title": "Take On Me",
        "artist": "a-ha",
        "format_type": "single",
        "category_slug": "pop-essentials",
        "price": Decimal("92.00"),
        "stock": 12,
        "seller_key": "registered_user",
        "status": ProductStatus.APPROVED,
        "release_date": date(1985, 10, 19),
        "description": "A bright synth-pop single with an instantly recognizable chorus and strong eighties nostalgia.",
    },
    {
        "title": "Future Nostalgia",
        "artist": "Dua Lipa",
        "format_type": "album",
        "category_slug": "pop-essentials",
        "price": Decimal("182.00"),
        "stock": 7,
        "seller_key": "retailer",
        "status": ProductStatus.PENDING,
        "release_date": date(2020, 3, 27),
        "description": "A dance-pop album with glossy production, disco influence, and strong demand among modern collectors.",
    },
    {
        "title": "Back to Black",
        "artist": "Amy Winehouse",
        "format_type": "album",
        "category_slug": "soul-rnb",
        "price": Decimal("184.00"),
        "stock": 6,
        "seller_key": "retailer",
        "status": ProductStatus.APPROVED,
        "release_date": date(2006, 10, 27),
        "description": "A modern soul classic with expressive vocals, sharp songwriting, and a distinctive retro tone.",
    },
    {
        "title": "Songs in the Key of Life",
        "artist": "Stevie Wonder",
        "format_type": "album",
        "category_slug": "soul-rnb",
        "price": Decimal("238.00"),
        "stock": 3,
        "seller_key": "registered_user",
        "status": ProductStatus.APPROVED,
        "release_date": date(1976, 9, 28),
        "description": "A sweeping Stevie Wonder album with rich arrangements, deep grooves, and premium collector appeal.",
    },
    {
        "title": "My Dear Melancholy,",
        "artist": "The Weeknd",
        "format_type": "ep",
        "category_slug": "soul-rnb",
        "price": Decimal("126.00"),
        "stock": 8,
        "seller_key": "registered_user",
        "status": ProductStatus.APPROVED,
        "release_date": date(2018, 3, 30),
        "description": "A moody R&B EP with atmospheric production, concise sequencing, and late-night listening appeal.",
    },
    {
        "title": "Random Access Memories",
        "artist": "Daft Punk",
        "format_type": "album",
        "category_slug": "electronic-dance",
        "price": Decimal("214.00"),
        "stock": 5,
        "seller_key": "retailer",
        "status": ProductStatus.APPROVED,
        "release_date": date(2013, 5, 17),
        "description": "A sleek electronic album blending live instrumentation, dance-floor energy, and audiophile-friendly production.",
    },
    {
        "title": "Discovery",
        "artist": "Daft Punk",
        "format_type": "album",
        "category_slug": "electronic-dance",
        "price": Decimal("172.00"),
        "stock": 7,
        "seller_key": "registered_user",
        "status": ProductStatus.APPROVED,
        "release_date": date(2001, 3, 12),
        "description": "A colorful Daft Punk release filled with French house textures, playful hooks, and club-era nostalgia.",
    },
    {
        "title": "Midnight City",
        "artist": "M83",
        "format_type": "single",
        "category_slug": "electronic-dance",
        "price": Decimal("88.00"),
        "stock": 10,
        "seller_key": "retailer",
        "status": ProductStatus.REJECTED,
        "release_date": date(2011, 8, 16),
        "description": "A widescreen synth-pop single with a soaring hook, pulsing rhythm, and cinematic energy.",
    },
    {
        "title": "Kind of Blue",
        "artist": "Miles Davis",
        "format_type": "album",
        "category_slug": "jazz-corner",
        "price": Decimal("168.00"),
        "stock": 8,
        "seller_key": "registered_user",
        "status": ProductStatus.APPROVED,
        "release_date": date(1959, 8, 17),
        "description": "A definitive modal jazz recording with relaxed interplay, elegant solos, and essential collector status.",
    },
    {
        "title": "Blue Train",
        "artist": "John Coltrane",
        "format_type": "album",
        "category_slug": "jazz-corner",
        "price": Decimal("158.00"),
        "stock": 7,
        "seller_key": "retailer",
        "status": ProductStatus.APPROVED,
        "release_date": date(1958, 1, 1),
        "description": "A focused hard-bop session led by John Coltrane with rich tone, drive, and classic Blue Note character.",
    },
]


def ensure_category(spec: dict[str, object]) -> Category:
    category = db.session.scalar(db.select(Category).where(Category.slug == spec["slug"]))
    if category is None:
        category = Category(slug=str(spec["slug"]))
        db.session.add(category)

    category.name = str(spec["name"])
    category.description = str(spec["description"])
    return category


def upsert_admin(*, username: str, email: str, display_name: str, password: str) -> AdminUser:
    admin = db.session.scalar(db.select(AdminUser).where((AdminUser.username == username) | (AdminUser.email == email)))
    if admin is None:
        admin = AdminUser(username=username, email=email, display_name=display_name)
        admin.set_password(password)
        db.session.add(admin)
    else:
        admin.username = username
        admin.email = email
        admin.display_name = display_name
        if not admin.password_hash:
            admin.set_password(password)
    admin.is_active = True
    return admin


def upsert_registered_user(
    *,
    username: str,
    email: str,
    display_name: str,
    password: str,
    is_retailer: bool = False,
) -> RegisteredUser:
    user = db.session.scalar(
        db.select(RegisteredUser).where(
            (RegisteredUser.username == username)
            | (RegisteredUser.email == email)
            | (RegisteredUser.display_name == display_name)
        )
    )
    if user is None:
        user = RegisteredUser(
            username=username,
            email=email,
            display_name=display_name,
            is_retailer=is_retailer,
        )
        user.set_password(password)
        db.session.add(user)
    else:
        user.username = username
        user.email = email
        user.display_name = display_name
        user.is_retailer = is_retailer
        if not user.password_hash:
            user.set_password(password)
    user.is_active = True
    return user


def sync_products(retailer: RegisteredUser, registered_user: RegisteredUser) -> None:
    categories = {
        category.slug: category for category in db.session.scalars(db.select(Category).order_by(Category.id.asc())).all()
    }
    sellers = {
        "retailer": retailer,
        "registered_user": registered_user,
    }
    existing_by_title = {
        product.title: product for product in db.session.scalars(db.select(Product).order_by(Product.id.asc())).all()
    }

    for spec in LISTING_SPECS:
        product = existing_by_title.get(str(spec["title"]))
        if product is None:
            product = Product(title=str(spec["title"]))
            db.session.add(product)

        product.artist = str(spec["artist"])
        product.format_type = str(spec["format_type"])
        product.category = categories[str(spec["category_slug"])]
        product.price = Decimal(spec["price"])
        product.stock = int(spec["stock"])
        product.seller = sellers[str(spec["seller_key"])]
        product.approval_status = str(spec["status"])
        product.release_date = spec["release_date"]
        product.description = str(spec["description"])
        product.image_url = None


def ensure_core_data() -> None:
    for spec in CATEGORY_SPECS:
        ensure_category(spec)

    upsert_admin(
        username="admin",
        email="admin@musiconline.com",
        display_name="musicOnline Admin",
        password=DEFAULT_ACCOUNT_PASSWORD,
    )
    upsert_admin(
        username="moderator",
        email="moderator@musiconline.com",
        display_name="Content Moderator",
        password=DEFAULT_ACCOUNT_PASSWORD,
    )

    db.session.commit()


def ensure_demo_data() -> None:
    ensure_core_data()

    retailer = upsert_registered_user(
        username="vinylnova",
        email="vinylnova@musiconline.com",
        display_name="Vinyl Nova Records",
        password=DEFAULT_ACCOUNT_PASSWORD,
        is_retailer=True,
    )
    registered_user = upsert_registered_user(
        username="analogsoul",
        email="analogsoul@musiconline.com",
        display_name="Analog Soul Collector",
        password=DEFAULT_ACCOUNT_PASSWORD,
        is_retailer=False,
    )

    db.session.flush()
    sync_products(retailer, registered_user)
    db.session.commit()
