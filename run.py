from app import create_app
from app.db import get_db_connection  
from migrations.migrations import apply_migrations

app = create_app()

def setup_database():
    with app.app_context():  # Establish the application context
        db = get_db_connection()
        if db:
            apply_migrations(db)  # Only apply migrations if the connection is successful
        else:
            print("Failed to connect to the database.")

if __name__ == '__main__':
    setup_database()  # Set up the database before running the app
    app.run(debug=True)
