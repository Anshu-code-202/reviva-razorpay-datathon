import pytest

from app.db.session import SessionLocal


@pytest.fixture
def session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
