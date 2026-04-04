import sys
import os
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.persistence.session_db_sync import SessionDBSync
from src.core.config_loader import CONFIG

logging.basicConfig(level=logging.INFO)

def test_connection():
    print("--- LaRa DB Sync Verification ---")
    try:
        import mysql.connector
        print(f"SUCCESS: mysql-connector-python {mysql.connector.__version__} is installed.")
    except ImportError:
        print("FAILED: mysql-connector-python is NOT installed.")
        return

    sync = SessionDBSync.get()
    if not sync.pool:
        print("FAILED: Could not initialize MySQL pool. Check config/config.yaml and MySQL service.")
        return

    print(f"Testing session_start with child_id=1 and UUID=test-uuid-123...")
    try:
        session_id = sync.session_start("test-uuid-123", 1)
        if session_id:
            print(f"SUCCESS: Session started in DB with ID: {session_id}")
            
            # Clean up test data if possible, or just leave it for verification
            print("To verify, run: SELECT * FROM sessions WHERE session_uuid='test-uuid-123';")
        else:
            print("FAILED: session_start returned None. Check logs.")
    except Exception as e:
        print(f"FAILED: session_start raised exception: {e}")

if __name__ == "__main__":
    test_connection()
