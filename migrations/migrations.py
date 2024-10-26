import os
import mysql.connector
from app.db import execute_query  

# migrations/migrations.py

def run_migration(connection, migration_file):
    """Run a single migration SQL script."""
    try:
        with open(migration_file, 'r') as file:
            sql = file.read()
        execute_query(connection, sql)  # Execute the migration script
        connection.commit()  # Ensure changes are committed
        print(f"Migration from {migration_file} applied successfully.")
    except Exception as e:
        print(f"Failed to run migration from {migration_file}: {str(e)}")


def apply_migrations(db):
    """
    Apply all migrations in the migrations folder.
    
    Args:
        db: Database connection object that can execute queries.
    """
    migrations_dir = 'app/migrations'  # Ensure this matches your directory structure
    try:
        for filename in os.listdir(migrations_dir):
            if filename.endswith('.sql'):
                file_path = os.path.join(migrations_dir, filename)
                run_migration(db, file_path)
    except Exception as e:
        print(f"Error applying migrations: {str(e)}")


def run_migration(connection, migration_file):
    """Run the migration script from a SQL file."""
    with open(migration_file, 'r') as file:
        migration_script = file.read()

    try:
        cursor = connection.cursor()
        for statement in migration_script.split(';'):  # Execute each statement in the script
            statement = statement.strip()
            if statement:  # Only execute non-empty statements
                cursor.execute(statement)
        connection.commit()
        print("Migration executed successfully.")
    except mysql.connector.Error as err:
        print(f"Error executing migration: {err}")
    finally:
        cursor.close()

