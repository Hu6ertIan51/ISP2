from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect
import os
from .db import get_db_connection, fetch_one
from .models import User
from migrations.migrations import run_migration

def create_app():
    app = Flask(__name__)

    # Session handling
    app.secret_key = os.getenv('SECRET_KEY', 'thisproject')

    # Load configurations from environment variables
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_USER'] = os.getenv('DB_USER', 'root')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'edusense')

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Initialize CSRF protection
    csrf = CSRFProtect(app)  # Create and initialize CSRF instance

    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        """Load a user from the database."""
        connection = get_db_connection()
        query = "SELECT id, full_name, email, password, role, dob, mobile_number, gender FROM users WHERE id = %s"
        result = fetch_one(connection, query, (user_id,))
        if result:
            return User(
                user_id=result['id'],  # Use user_id instead of id
                full_name=result['full_name'],
                email=result['email'],
                password=result['password'],
                role=result['role'],
                dob=result['dob'],
                mobile_number=result['mobile_number'],
                gender=result['gender']
            )
        return None

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    # Run migrations within the app context
    with app.app_context():
        db_connection = get_db_connection()
        if db_connection:
            run_migration(db_connection, 'migrations/create_tables.sql')
        else:
            print("Failed to establish a database connection.")

    return app