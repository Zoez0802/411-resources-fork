from contextlib import contextmanager
import logging
import os
import sqlite3

from weather.utils.logger import configure_logger  

logger = logging.getLogger(__name__)
configure_logger(logger)

# Load the DB path from environment variable or use a default
DB_PATH = os.getenv("WEATHER_DB_PATH", "/app/sql/weather.db")


def check_database_connection():
    """
    Verifies that the weather database is accessible and responding.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        conn.close()
    except sqlite3.Error as e:
        error_message = f"Weather database connection error: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e


def check_table_exists(tablename: str):
    """
    Checks if a specific table exists in the weather database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (tablename,)
        )
        result = cursor.fetchone()
        conn.close()

        if result is None:
            error_message = f"Table '{tablename}' does not exist."
            logger.error(error_message)
            raise Exception(error_message)

    except sqlite3.Error as e:
        error_message = f"Table check error for '{tablename}': {e}"
        logger.error(error_message)
        raise Exception(error_message) from e


@contextmanager
def get_db_connection():
    """
    Context manager for safely acquiring and releasing a database connection.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection context error: {e}")
        raise e
    finally:
        if conn:
            conn.close()
