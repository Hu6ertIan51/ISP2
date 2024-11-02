from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash  # Import hash functions for password handling
from .db import fetch_one, execute_query  # Import the functions from db.py
import random  # Import the random module

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
        query = "SELECT * FROM users WHERE email = %s"
        result = fetch_one(db, query, (email,))
        if result:
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
        hashed_password = generate_password_hash(password)
        query = "INSERT INTO users (full_name, email, password, dob, mobile_number, gender, role) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        execute_query(db, query, (full_name, email, hashed_password, dob, mobile_number, gender, role))

    def check_password(self, password):
        """Check if the provided password matches the stored password."""
        if self.password.startswith("pbkdf2:sha256:"):
            return check_password_hash(self.password, password)
        else:
            return self.password == password

    def __repr__(self):
        return f"<User {self.full_name}, Role: {self.role}>"

import random
from app.db import fetch_one, execute_query  # Ensure these are properly imported

class Student:
    def __init__(self, user_id, school, course, admission_number, current_year, full_name = None):
        self.user_id = user_id
        self.school= school
        self.course = course
        self.admission_number = admission_number
        self.full_name = full_name
        self.current_year = current_year
        #self.year_intake = year_intake
        #self.education_status = education_status

    @staticmethod
    def generate_admission_number(db):
        """Generate a unique admission number."""
        while True:
            # Generate a random number between 100000 and 999999
            random_number = random.randint(100000, 999999)
            admission_number = f"A{random_number}"  # Prefix with 'A'

            # Check if the admission number already exists
            query = "SELECT COUNT(*) AS count FROM student_details WHERE admission_number = %s"
            result = fetch_one(db, query, (admission_number,))

            if result['count'] == 0:  # Unique admission number found
                return admission_number

    @staticmethod
    def create_student(user_id, school, course, admission_number, current_year, db):
        admission_number = Student.generate_admission_number(db)
        query = """
        INSERT INTO student_details (user_id, school, course, admission_number, current_year)
        VALUES (%s,%s,%s,%s,%s)
        """
        params = (user_id, school, course, admission_number, current_year)
        execute_query(db, query, params)

    @staticmethod
    def find_by_user_id(user_id, db):
        """Query student details by user ID, including the student's name."""
        query = """
        SELECT u.full_name, sd.user_id, sd.school, sd.course, sd.admission_number, sd.current_year
        FROM student_details sd
        JOIN users u ON sd.user_id = u.id
        WHERE sd.user_id = %s
        """
        result = fetch_one(db, query, (user_id,))
        if result:
            return Student(
                user_id=result['user_id'],
                school=result['school'],
                course=result['course'],
                admission_number=result['admission_number'],
                full_name=result['full_name'],
                current_year=result['current_year']
            )
        return None



