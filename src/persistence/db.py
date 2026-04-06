import mysql.connector
from mysql.connector import pooling
import logging
from threading import Lock

try:
    from src.core.config_loader import CONFIG
    _DB_CFG = CONFIG.get("mysql", {})
    DB_HOST = _DB_CFG.get("host", "localhost")
    DB_PORT = _DB_CFG.get("port", 3306)
    DB_USER = _DB_CFG.get("user", "root")
    DB_PASS = _DB_CFG.get("password", "")
    DB_NAME = _DB_CFG.get("database", "lara_dashboard")
    POOL_SIZE = _DB_CFG.get("pool_size", 10)
except Exception:
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASS = ""
    DB_NAME = "lara_dashboard"
    POOL_SIZE = 10

class Database:
    _instance = None
    _lock = Lock()

    def __init__(self):
        if Database._instance is not None:
            raise RuntimeError("Database is a singleton. Use get()")
        
        self.pool = None
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="lara_main_pool",
                pool_size=POOL_SIZE,
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME
            )
            logging.info(f"[DB] MySQL Pool initialized: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        except Exception as e:
            logging.error(f"[DB] Failed to initialize MySQL Pool: {e}")

    @classmethod
    def get(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = Database()
        return cls._instance

    def execute(self, query, params=None, commit=True):
        """Execute a query and return lastrowid or affected rows count."""
        if not self.pool:
            logging.error("[DB] No connection pool available.")
            return None
        
        conn = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            result = None
            if commit:
                conn.commit()
                result = cursor.lastrowid if cursor.lastrowid != 0 else cursor.rowcount
            
            cursor.close()
            return result
        except Exception as e:
            logging.error(f"[DB] Execute failed: {query} | Error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def fetch_one(self, query, params=None):
        """Fetch a single row as a dictionary."""
        if not self.pool:
            return None
        
        conn = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            logging.error(f"[DB] FetchOne failed: {query} | Error: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def fetch_all(self, query, params=None):
        """Fetch all rows as a list of dictionaries."""
        if not self.pool:
            return []
        
        conn = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logging.error(f"[DB] FetchAll failed: {query} | Error: {e}")
            return []
        finally:
            if conn:
                conn.close()
