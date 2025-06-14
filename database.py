import os
import psycopg2
import psycopg2.extras
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger('vault.database')

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('PGHOST'),
            'port': os.getenv('PGPORT', 5432),
            'database': os.getenv('PGDATABASE'),
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
        }
        
        # Check if all required environment variables are set
        required_vars = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def initialize_schema(self):
        """Initialize the database schema"""
        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
                conn.commit()
                logger.info("Database schema initialized successfully")
    
    def set_user_data(self, user_id: str, key: str, value: str) -> bool:
        """Set user data (upsert operation)"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_data (user_id, key, value) 
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, key) 
                        DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
                    """, (user_id, key, value))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Error setting user data: {e}")
            return False
    
    def get_user_data(self, user_id: str, key: Optional[str] = None) -> Optional[Any]:
        """Get user data"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    if key is None:
                        # Get all data for user
                        cursor.execute("SELECT key, value FROM user_data WHERE user_id = %s", (user_id,))
                        rows = cursor.fetchall()
                        if not rows:
                            return None
                        return {row['key']: row['value'] for row in rows}
                    else:
                        # Get specific key for user
                        cursor.execute("SELECT value FROM user_data WHERE user_id = %s AND key = %s", (user_id, key))
                        row = cursor.fetchone()
                        return row['value'] if row else None
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return None
    
    def delete_user_data(self, user_id: str, key: str) -> bool:
        """Delete specific user data"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM user_data WHERE user_id = %s AND key = %s", (user_id, key))
                    affected_rows = cursor.rowcount
                    conn.commit()
                    return affected_rows > 0
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False
    
    def get_user_data_count(self, user_id: str) -> int:
        """Get count of user data entries"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM user_data WHERE user_id = %s", (user_id,))
                    return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting user data count: {e}")
            return 0
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False