# MusicOnline

MusicOnline is a Flask-based vinyl marketplace prototype aligned to the project PDF, with a lightweight no-payment order flow added on top of the brief:

- new user registration
- user and administrator sign in
- vinyl search by artist or record title
- record detail pages
- placeholder advertisement graphics for future relevant ads
- add to bag and create prototype orders without payment
- registered-user listing create, edit, and delete
- administrator review of submitted listings
- basic session and form security

## Database Design

The project now targets a clean MySQL database named `musiconline`.

Core tables:

- `admin_users`
- `registered_users`
- `music_categories`
- `music_listings`
- `shopping_cart_items`
- `customer_orders`
- `customer_order_items`

Why this is 3NF-friendly:

- administrator and registered-user data are separated into their own entities
- listing records reference sellers and categories by foreign key instead of duplicating account data
- category descriptions live in a lookup table rather than being repeated across every listing row
- non-key attributes depend on the key of their own table, with cart rows, order headers, and order line items split into separate entities instead of being mixed into listing or account tables

Reference SQL file:

- `musiconline.sql`

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Initialize the local development database and demo data:

```bash
python -m flask --app run.py init-db --with-demo
```

This step is optional when using the default SQLite setup and starting with `python run.py`; the app will create the local demo database automatically if it is missing.

3. Start the development server:

```bash
python run.py
```

4. Open `http://127.0.0.1:5000`

## Demo Accounts

- `admin / 123456`
- `moderator / 123456`
- `vinylnova / 123456`
- `analogsoul / 123456`

## MySQL Configuration

The app reads `DATABASE_URL` from `.env`.

Example:

```env
DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/musiconline?charset=utf8mb4
```

If `.env` is not present, the app uses the local SQLite database at `instance/musiconline.db`.
