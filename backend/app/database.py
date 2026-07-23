import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from urllib.parse import urlparse
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Connection pool setup
db_pool = None

def _parse_db_url(url: str) -> dict:
    """Parse DATABASE_URL into psycopg2 keyword arguments, adding client_encoding=UTF8."""
    p = urlparse(url)
    return {
        "host": p.hostname,
        "port": p.port or 5432,
        "user": p.username,
        "password": p.password,
        "dbname": p.path.lstrip("/"),
        "client_encoding": "UTF8",
    }

def init_db_pool():
    global db_pool
    if db_pool is None:
        try:
            conn_kwargs = _parse_db_url(settings.DATABASE_URL)
            db_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                **conn_kwargs
            )
            logger.info("PostgreSQL ThreadedConnectionPool initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection pool: {e}")

def close_db_pool():
    global db_pool
    if db_pool is not None:
        db_pool.closeall()
        logger.info("PostgreSQL ConnectionPool closed.")
        db_pool = None

@contextmanager
def get_db_connection():
    """
    Yields a connection from the pool. Automatically commits on success
    and rolls back transaction on error.
    """
    global db_pool
    if db_pool is None:
        init_db_pool()
    
    conn = db_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction error (rolled back): {e}")
        raise e
    finally:
        db_pool.putconn(conn)

@contextmanager
def get_db_cursor():
    """
    Yields a cursor from a connection pool instance.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            yield cur
