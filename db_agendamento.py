import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Database connection parameters
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")
DB_USER = os.getenv("PGUSER", "postgres")
DB_PASSWORD = os.getenv("PGPASSWORD", "xbala")
DB_NAME = os.getenv("PGDATABASE", "db_sa")

def get_database_url():
    """Return the database URL for SQLAlchemy"""
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def test_connection():
    """Test database connection"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logging.info(f"Database connection successful. PostgreSQL version: {version}")
            return True
        except Exception as e:
            logging.error(f"Database test error: {e}")
            return False
        finally:
            conn.close()
    return False

def execute_query(query, params=None):
    """Execute a query and return results"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return results
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        logging.error(f"Query execution error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()
