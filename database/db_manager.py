import mysql.connector
from mysql.connector import Error, errorcode, pooling
import os


class DatabaseManager:
    def __init__(self, pool_name="mypool", pool_size=3):
        try:
            env_pool_size = os.environ.get("DB_CONNECTIONS", pool_size)
            final_pool_size = int(env_pool_size)
        except ValueError:
            final_pool_size = pool_size
            print(
                f"Warning: Invalid DB_CONNECTIONS value. Using default pool_size={pool_size}."
            )
        self.pool_name = pool_name
        self.pool_size = final_pool_size
        self.pool = self.create_pool(pool_name, final_pool_size)

    def create_pool(self, pool_name, pool_size):
        """Create a connection pool."""
        try:
            pool = pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                pool_reset_session=True,
                host=os.getenv("DATABASE_HOST"),
                port=os.getenv("DATABASE_PORT"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASS"),
                database=os.getenv("DATABASE_DB"),
                autocommit=False,
                buffered=True,
            )
            print(f"Connection pool established, with size: {pool_size}")
            return pool
        except Error as e:
            print(f"Error creating connection pool: {e}")
            return None

    def get_connection(self):
        """Get a connection from the pool."""
        try:
            return self.pool.get_connection()
        except AttributeError:
            print("Connection pool is not created.")
            self.pool = self.create_pool(
                self.pool_name, self.pool_size
            )  # re-create pool
            return self.pool.get_connection()
        except Error as e:
            print(f"Error getting connection from pool: {e}")

    def execute_query(self, sql, params=None, commit=False):
        """Execute a given SQL query using a connection from the pool."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            if commit:
                conn.commit()
            return cursor
        except Error as e:
            print(f"Error executing query: {e}")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def fetch_one(self, sql, params=None):
        """Fetch a single row from a query."""
        cursor = self.execute_query(sql, params)
        if cursor:
            result = cursor.fetchone()
            return result
        return None

    def update(self, sql, params=None):
        """Update data in the database."""
        self.execute_query(sql, params, commit=True)

    def insert(self, sql, params=None):
        """Insert data into the database."""
        self.execute_query(sql, params, commit=True)

    def delete(self, sql, params=None):
        """Delete data from the database."""
        self.execute_query(sql, params, commit=True)

    def begin_transaction(self, conn):
        """Begin a transaction."""
        try:
            conn.start_transaction()
        except Error as e:
            print(f"Error beginning transaction: {e}")
            raise

    def commit_transaction(self, conn):
        """Commit a transaction."""
        try:
            conn.commit()
        except Error as e:
            print(f"Error committing transaction: {e}")
            raise

    def rollback_transaction(self, conn):
        """Rollback a transaction."""
        try:
            conn.rollback()
        except Error as e:
            print(f"Error rolling back transaction: {e}")
            raise
