# app/db.py
import mysql.connector
import os

def get_db_connection():
    """Establish a database connection using environment variables for configuration."""
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'edusense')
    )
    return connection

def execute_query(connection, query, params=None):
    """Execute a query against the database."""
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()  # Commit the changes if needed
    cursor.close()

def fetch_one(connection, query, params=None):
    """Fetch a single record from the database."""
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    return result
