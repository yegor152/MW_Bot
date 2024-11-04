import mysql.connector
from mysql.connector import pooling
from typing import Optional
import logging
from config import DB_CONFIG


class DatabasePool:
    _instance = None
    _pool = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabasePool()
        return cls._instance

    def __init__(self):
        if DatabasePool._pool is None:
            try:
                DatabasePool._pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=5,
                    **DB_CONFIG
                )
            except Exception as e:
                logging.error(f"Error creating connection pool: {e}")
                raise

    def get_connection(self):
        return DatabasePool._pool.get_connection()
