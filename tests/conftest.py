import pytest
import psycopg

from app.config import DATABASE_URL


@pytest.fixture
def db_connection():
    conn = psycopg.connect(DATABASE_URL)

    try:
        yield conn
    finally:
        conn.close()