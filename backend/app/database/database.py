"""Database Engine, Session Factory, and Base Model.

Responsibilities:
- Creates the SQLAlchemy engine (supports SQLite and PostgreSQL via DATABASE_URL).
- Provides a thread-safe session factory (SessionLocal).
- Exposes DeclarativeBase for all ORM models.
- Exposes get_db() generator for FastAPI dependency injection.

Integration:
- Used by all repositories.
- Used by app/dependencies.py to inject DB sessions.
- Called from app/main.py lifespan to initialize tables.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.pool import StaticPool
from app.config import settings
from app.utils.logger import logger


def _build_engine():
    """Build SQLAlchemy engine with settings appropriate for the configured database."""
    url = settings.DATABASE_URL
    is_sqlite = url.startswith("sqlite")

    if is_sqlite:
        # SQLite: use StaticPool so the same connection is reused across threads
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.DB_ECHO,
        )
        # Enable WAL mode and foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragmas(dbapi_conn, _):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        # PostgreSQL / other: use connection pooling
        engine = create_engine(
            url,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_pre_ping=True,       # verify connections on checkout
            echo=settings.DB_ECHO,
        )

    return engine


engine = _build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""
    pass


def init_db() -> None:
    """Create all tables defined via ORM models.

    Called during application startup. Safe to call multiple times (CREATE IF NOT EXISTS).
    For production schema management, use Alembic migrations instead.
    """
    from app.database import models  # noqa: F401 — ensures models are registered
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")


def get_db():
    """FastAPI dependency that yields a SQLAlchemy session and closes it after the request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
