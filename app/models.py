from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash  # Import hash functions for password handling
from .db import fetch_one, execute_query  # Import the functions from db.py

class User(UserMixin):  # Inherit from UserMixin
    def __init__(self, user_id, full_name, email, password, dob, mobile_number, gender, role):  
        self.id = user_id  
        self.full_name = full_name
        self.email = email
        self.password = password  
        self.dob = dob  
        self.mobile_number = mobile_number  
        self.gender = gender 
        self.role = role  

    @staticmethod
    def find_by_email(email, db):
        """Query user by email."""
        query = "SELECT * FROM users WHERE email = %s"  # Ensure the correct table name
        result = fetch_one(db, query, (email,))  # Use fetch_one with db connection
        if result:
            # Create User object without age
            return User(
                user_id=result['id'],
                full_name=result['full_name'],
                email=result['email'],
                password=result['password'],
                dob=result['dob'],
                mobile_number=result['mobile_number'],
                gender=result['gender'],
                role=result['role']
            )
        return None


    @staticmethod
    def create_user(full_name, email, password, dob, mobile_number, gender, role, db):
        """Insert a new user into the database."""
        hashed_password = generate_password_hash(password)  # Hash the password before saving
        # Remove 'age' from the SQL query
        query = "INSERT INTO users (full_name, email, password, dob, mobile_number, gender, role) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        # Adjust the parameters tuple to match the SQL query
        execute_query(db, query, (full_name, email, hashed_password, dob, mobile_number, gender, role))


    def check_password(self, password):
        """Check if the provided password matches the stored password, supporting both hashed and plain text."""
        print("Stored password:", self.password)  # Debugging: shows the stored password
        print("Entered password:", password)  # Debugging: shows the entered password
        
        if self.password.startswith("pbkdf2:sha256:"):  # Check if stored password is hashed
            return check_password_hash(self.password, password)  # Check using the hash function
        else:
            return self.password == password  # Compare plain text passwords

    def __repr__(self):
        return f"<User {self.full_name}, Role: {self.role}>"
