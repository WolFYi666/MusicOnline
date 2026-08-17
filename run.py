from sqlalchemy import inspect

from app import create_app
from app.extensions import db
from app.schema import ensure_schema_updates
from app.seed import ensure_core_data, ensure_demo_data


app = create_app()


def ensure_local_sqlite_database() -> None:
    database_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not database_uri.startswith("sqlite:///"):
        return

    with app.app_context():
        inspector = inspect(db.engine)
        if inspector.has_table("music_listings"):
            return
        db.create_all()
        ensure_schema_updates()
        ensure_core_data()
        ensure_demo_data()


if __name__ == "__main__":
    ensure_local_sqlite_database()
    app.run(debug=True)
