from typing import Optional, Dict
import logging
from .database import DatabasePool


class UserManager:
    def __init__(self):
        self.db_pool = DatabasePool.get_instance()
        self.registration_states: Dict[int, str] = {}
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database with proper schema"""
        try:
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        chat_id BIGINT PRIMARY KEY,
                        name VARCHAR(255),
                        phone VARCHAR(20),
                        username VARCHAR(255),
                        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
            raise

    def initialize_user(self, chat_id: int, username: Optional[str] = None) -> bool:
        """Create initial user record with chat_id and username"""
        try:
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT IGNORE INTO users (chat_id, username)
                    VALUES (%s, %s)
                """, (chat_id, username))

                conn.commit()
                return True

        except Exception as e:
            logging.error(f"Error initializing user: {e}")
            return False

    def update_user_info(self, chat_id: int, name: Optional[str] = None,
                         phone: Optional[str] = None) -> bool:
        """Update user information"""
        try:
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()

                # First check if user exists
                cursor.execute("SELECT chat_id FROM users WHERE chat_id = %s", (chat_id,))
                if not cursor.fetchone():
                    logging.warning(f"Attempted to update non-existent user: {chat_id}")
                    return False

                update_fields = []
                params = []

                if name is not None:
                    update_fields.append("name = %s")
                    params.append(name)
                if phone is not None:
                    update_fields.append("phone = %s")
                    params.append(phone)

                if not update_fields:
                    return False

                params.append(chat_id)

                query = f"""
                    UPDATE users 
                    SET {', '.join(update_fields)}
                    WHERE chat_id = %s
                """
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logging.error(f"Error updating user info: {e}")
            return False

    def has_complete_profile(self, chat_id: int) -> bool:
        """Check if user has both name and phone"""
        try:
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 1 
                    FROM users 
                    WHERE chat_id = %s 
                    AND name IS NOT NULL 
                    AND phone IS NOT NULL
                """, (chat_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"Error checking user profile: {e}")
            return False

    def get_user_details(self, chat_id: int) -> Optional[Dict]:
        """Get user details for admin notification"""
        try:
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT name, phone, username, registration_date
                    FROM users 
                    WHERE chat_id = %s
                """, (chat_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Error getting user details: {e}")
            return None

    def get_user(self, chat_id: int) -> Optional[Dict]:
        """Get user information"""
        try:
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT chat_id, name, phone, username, registration_date
                    FROM users WHERE chat_id = %s
                """, (chat_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Error getting user: {e}")
            return None