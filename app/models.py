from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash  # Import hash functions for password handling
from .db import fetch_one, fetch_all, execute_query  # Import the functions from db.py
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
    def __init__(self, user_id, school, course, admission_number, current_year, year_intake, academic_status, full_name = None, mobile_number = None, email = None):
        self.user_id = user_id
        self.school= school
        self.course = course
        self.admission_number = admission_number
        self.full_name = full_name
        self.current_year = current_year
        self.mobile_number = mobile_number
        self.email = email
        self.year_intake = year_intake
        self.academic_status = academic_status

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
    def create_student(user_id, school, course, admission_number, current_year, year_intake, academic_status, db):
        admission_number = Student.generate_admission_number(db)
        query = """
        INSERT INTO student_details (user_id, school, course, admission_number, current_year, year_intake, academic_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """
        params = (user_id, school, course, admission_number, current_year, year_intake, academic_status)
        execute_query(db, query, params)

    @staticmethod
    def find_by_user_id(user_id, db):
        """Query student details by user ID, including the student's name."""
        query = """
        SELECT u.full_name, sd.user_id, sd.school, sd.course, sd.admission_number, sd.current_year, u.mobile_number, u.email, sd.year_intake, sd.academic_status
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
                current_year=result['current_year'],
                mobile_number=result['mobile_number'],
                email=result['email'],
                year_intake=result['year_intake'],
                academic_status=result['academic_status']
            )
        return None
    
    @staticmethod
    def get_all_students(db):
        """Fetch all student details along with user info."""
        query = """
        SELECT u.full_name, sd.user_id, sd.school, sd.course, sd.admission_number, sd.current_year, 
            u.mobile_number, u.email, sd.year_intake, sd.academic_status
        FROM student_details sd
        JOIN users u ON sd.user_id = u.id
        """
        results = fetch_all(db, query)
        students = []
        for result in results:
            # Convert the academic_status from 0/1 to 'active'/'inactive'
            academic_status = 'Inactive' if result['academic_status'] == 1 else 'Active'
            
            student = Student(
                user_id=result['user_id'],
                school=result['school'],
                course=result['course'],
                admission_number=result['admission_number'],
                full_name=result['full_name'],
                current_year=result['current_year'],
                year_intake=result['year_intake'],
                academic_status=academic_status  # Store 'active' or 'inactive'
            )
            students.append(student)
        
        return students

class Lecturer:
    def __init__(self, user_id, school, lecturer_number, year_intake, lecturer_status, full_name=None, mobile_number=None, email=None):
        self.user_id = user_id
        self.school = school
        self.lecturer_number = lecturer_number
        self.year_intake = year_intake
        self.lecturer_status = lecturer_status
        self.full_name = full_name
        self.mobile_number = mobile_number
        self.email = email

    @staticmethod
    def generate_lecturer_number(db):
        """Generate a unique lecturer number."""
        while True:
            random_number = random.randint(100000, 999999)
            lecturer_number = f"L{random_number}"  # Prefix with 'L'

            # Check if the lecturer number already exists
            query = "SELECT COUNT(*) AS count FROM lecturer_details WHERE lecturer_number = %s"
            result = fetch_one(db, query, (lecturer_number,))

            if result['count'] == 0:  # Unique lecturer number found
                return lecturer_number

    @staticmethod
    def create_lecturer(user_id, school, lecturer_number, year_intake, lecturer_status, db):
        lecturer_number = Lecturer.generate_lecturer_number(db)
        query = """
        INSERT INTO lecturer_details (user_id, school, lecturer_number, year_intake, lecturer_status)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, school, lecturer_number, year_intake, lecturer_status)
        execute_query(db, query, params)

    @staticmethod
    def find_by_user_id(user_id, db):
        """Query lecturer details by user ID, including the lecturer's name."""
        query = """
        SELECT u.full_name, ld.user_id, ld.school, ld.lecturer_number, u.mobile_number, u.email, ld.year_intake, ld.lecturer_status
        FROM lecturer_details ld
        JOIN users u ON ld.user_id = u.id 
        WHERE ld.user_id = %s
        """
        result = fetch_one(db, query, (user_id,))
        if result:
            return Lecturer(
                user_id=result['user_id'],
                school=result['school'],
                lecturer_number=result['lecturer_number'],
                full_name=result['full_name'],
                mobile_number=result['mobile_number'],
                email=result['email'],
                year_intake=result['year_intake'],
                lecturer_status=result['lecturer_status']
            )
        return None
    
    @staticmethod
    def convert_lecturer_status(status):
        """Convert lecturer status from 0/1 to 'active'/'inactive'."""
        return 'Inactive' if status == 1 else 'Active'

    @staticmethod
    def get_all_lecturers(db):
        """Fetch all lecturers and their details along with user info."""
        query = """
        SELECT u.full_name, ld.user_id, ld.school, ld.lecturer_number, u.mobile_number, u.email, ld.year_intake, ld.lecturer_status
        FROM lecturer_details ld
        JOIN users u ON ld.user_id = u.id
        """
        results = fetch_all(db, query)
        lecturers = []
        for result in results:
            # Convert lecturer_status to meaningful 'active'/'inactive'
            lecturer_status = Lecturer.convert_lecturer_status(result['lecturer_status'])
            
            lecturer = Lecturer(
                user_id=result['user_id'],
                school=result['school'],
                lecturer_number=result['lecturer_number'],
                full_name=result['full_name'],
                email=result['email'],
                year_intake=result['year_intake'],
                lecturer_status=lecturer_status
            )
            lecturers.append(lecturer)
        return lecturers
    
class Unit:
    def __init__(self, unit_name, unit_code, school, course, year_offered, semester_offered):
        self.unit_name = unit_name
        self.unit_code = unit_code
        self.school = school
        self.course = course
        self.year_offered = year_offered
        self.semester_offered = semester_offered

    
    def generate_unit_code(unit_name, course, year_offered, semester_offered, db):
        # Generate a base code from the first three letters of the unit name
        unit_name_code = ''.join(word[0] for word in unit_name.split()[:3]).upper()
        
        # Use the first three letters of the course and the last two digits of the year offered
        course_code = ''.join(word[0] for word in course.split()[:3]).upper()
        year_code = str(year_offered)[-2:]
        
        # Add a semester code (S1 for Semester 1, S2 for Semester 2)
        semester_code = f"S{semester_offered}"

        # Construct a base code using unit name, course, year offered, and semester (e.g., AI10124S1)
        base_code = f"{unit_name_code}{course_code}{year_code}{semester_code}"

        # Check the database for existing codes and increment if necessary
        query = """
        SELECT COUNT(*) FROM units WHERE unit_code LIKE %s
        """
        params = (f"{base_code}%",)
        result = fetch_all(db, query, params)

        # Check if result is valid and has expected data
        if result and isinstance(result, list) and len(result) > 0:
            # Access the count from the first tuple in the result
            count = result[0][0] if result[0] and isinstance(result[0], tuple) else 0
        else:
            count = 0  # If no results, set count to 0
        
        # Append the count to the base code for uniqueness
        unique_code = f"{base_code}{count + 1:03d}"  # e.g., AI10124S1001
        return unique_code

    @staticmethod
    def create_unit(unit_name, unit_code, school, course, year_offered, semester_offered, db):
        query = """
        INSERT INTO units (unit_name, unit_code, school, course, year_offered, semester_offered)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (unit_name, unit_code, school,course, year_offered, semester_offered)
        execute_query(db, query, params)

    @staticmethod
    def get_all_units(db):
        """Fetch all units from the database."""
        query = """
        SELECT unit_name, unit_code, school, course, year_offered, semester_offered
        FROM units
        """
        results = fetch_all(db, query)
        units = []
        for result in results:
            unit = Unit(
                unit_name=result['unit_name'],
                unit_code=result['unit_code'],
                school=result['school'],
                course=result['course'],
                year_offered=result['year_offered'],
                semester_offered=result['semester_offered']
            )
            units.append(unit)
        return units
