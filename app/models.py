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
    
class SystemAdmin:
    def __init__(self, user_id, staff_number, year_registered, admin_status, full_name=None, mobile_number=None, email=None):
        self.user_id = user_id
        self.staff_number = staff_number
        self.year_registered = year_registered
        self.admin_status = admin_status
        self.full_name = full_name
        self.mobile_number = mobile_number
        self.email = email


    @staticmethod
    def generate_staff_number(db):
        """Generate a unique staff number."""
        while True:
            random_number = random.randint(1000, 9999)
            staff_number = f"SA-{random_number}"  # Prefix with 'S'

            # Check if the staff number already exists
            query = "SELECT COUNT(*) AS count FROM sysadmin WHERE staff_number = %s"
            result = fetch_one(db, query, (staff_number,))

            if result['count'] == 0:  # Unique staff number found
                return staff_number
    
    @staticmethod
    def create_system_admin(user_id, staff_number, year_registered, admin_status, db):
        staff_number = SystemAdmin.generate_staff_number(db)
        query = """
        INSERT INTO sysadmin (user_id, staff_number, year_registered, admin_status)
        VALUES (%s, %s, %s, %s)
        """
        params = (user_id, staff_number, year_registered, admin_status)
        execute_query(db, query, params)

    @staticmethod
    def find_by_user_id(user_id, db):
        """Query admin details by user ID, including the admin's name."""
        query = """
        SELECT u.full_name, sa.user_id, sa.staff_number, sa.year_registered, u.mobile_number, u.email, sa.admin_status
        FROM sysadmin sa
        JOIN users u ON sa.user_id = u.id
        WHERE sa.user_id = %s
        """
        result = fetch_one(db, query, (user_id,))
        if result:
            return SystemAdmin(
                user_id=result['user_id'],
                staff_number=result['staff_number'],
                full_name=result['full_name'],
                year_registered=result['year_registered'],
                mobile_number=result['mobile_number'],
                email=result['email'],
                admin_status=result['admin_status']
            )
        return None

class Student:
    def __init__(self, id, user_id, school, course, admission_number, current_year, year_intake, international, academic_status, full_name = None, mobile_number = None, email = None):
        self.id = id
        self.user_id = user_id
        self.school= school
        self.course = course
        self.admission_number = admission_number
        self.full_name = full_name
        self.current_year = current_year
        self.mobile_number = mobile_number
        self.email = email
        self.year_intake = year_intake
        self.international = international
        self.academic_status = academic_status


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
    def create_student(user_id, school, course, admission_number, current_year, year_intake, international, academic_status, db):
        admission_number = Student.generate_admission_number(db)
        query = """
        INSERT INTO student_details (user_id, school, course, admission_number, current_year, year_intake, international, academic_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        params = (user_id, school, course, admission_number, current_year, year_intake, international, academic_status)
        execute_query(db, query, params)

    @staticmethod
    def find_by_user_id(user_id, db):
        """Query student details by user ID, including the student's name."""
        query = """ 
        SELECT u.full_name, sd.id, sd.user_id, sd.school, sd.course, sd.admission_number, 
            sd.current_year, u.mobile_number, u.email, sd.year_intake, sd.international, 
            sd.academic_status
        FROM student_details sd
        JOIN users u ON sd.user_id = u.id
        WHERE sd.user_id = %s
        """
        result = fetch_one(db, query, (user_id,))
        
        if result:
            # Create a Student object with attributes from the result
            student = Student(
                id=result['id'],
                user_id=result['user_id'],
                school=result['school'],
                course=result['course'],
                admission_number=result['admission_number'],
                full_name=result['full_name'],
                current_year=result['current_year'],
                mobile_number=result['mobile_number'],
                email=result['email'],
                year_intake=result['year_intake'],
                international=result['international'],
                academic_status=result['academic_status']
            )
            return student 
        
        return None

    
    @staticmethod
    def find_by_student_id(db, user_id):
        """Query student details by user ID, including the student's name and add id attribute."""
        query = """
        SELECT u.id, u.full_name, sd.user_id, sd.school, sd.course, sd.admission_number, sd.current_year, u.mobile_number, u.email, sd.year_intake, sd.international, sd.academic_status
        FROM student_details sd
        JOIN users u ON sd.user_id = u.id
        WHERE sd.user_id = %s
        """
        result = fetch_one(db, query, (user_id,))
        if result:
            return Student(
                id=result['id'], 
                user_id=result['user_id'],
                school=result['school'],
                course=result['course'],
                admission_number=result['admission_number'],
                full_name=result['full_name'],
                current_year=result['current_year'],
                mobile_number=result['mobile_number'],
                email=result['email'],
                year_intake=result['year_intake'],
                international=result['international'],
                academic_status=result['academic_status']
            )
        return None

    
    @staticmethod
    def get_units_for_student(db, user_id, status="Active"):
        """
        Fetch all active units for the course associated with the given user ID.
        """
        # First, retrieve the user's course
        course_query = "SELECT course FROM student_details WHERE user_id = %s"
        course_result = fetch_one(db, course_query, (user_id,))
        user_course = course_result['course'] if course_result else None

        # If no course is found, return an empty list
        if not user_course:
            return []

        # Now fetch the units based on the user's course and status
        units_query = """
        SELECT id, unit_name, unit_code, school, course, year_offered, semester_offered, status
        FROM units
        WHERE status = %s AND course = %s
        """
        units_params = (status, user_course)
        results = fetch_all(db, units_query, units_params)

        # Process and return units
        units = [
            Unit(
                id=result['id'],
                unit_name=result['unit_name'],
                unit_code=result['unit_code'],
                school=result['school'],
                course=result['course'],
                year_offered=result['year_offered'],
                semester_offered=result['semester_offered'],
                status=result['status']
            )
            for result in results
        ]
        return units

    @staticmethod
    def get_all_students(db):
        """Fetch all student details along with user info."""
        query = """
        SELECT u.id, u.full_name, sd.user_id, sd.school, sd.course, sd.admission_number, sd.current_year, 
            u.mobile_number, u.email, sd.year_intake, sd.academic_status, sd.international
        FROM student_details sd
        JOIN users u ON sd.user_id = u.id
        """
        results = fetch_all(db, query)
        students = []
        for result in results:
            # Convert the academic_status from 0/1 to 'active'/'inactive'
            academic_status = 'Inactive' if result['academic_status'] == 1 else 'Active'
            
            # Convert the international column (0 or 1) to 'Domestic Residency' or 'International Residency'
            residency_status = 'International Residency' if result['international'] == 1 else 'Domestic Residency'
            
            student = Student(
                id=result['id'],
                user_id=result['user_id'],
                school=result['school'],
                course=result['course'],
                admission_number=result['admission_number'],
                full_name=result['full_name'],
                current_year=result['current_year'],
                year_intake=result['year_intake'],
                international=residency_status,  # Set the converted residency status
                academic_status=academic_status  # Store 'active' or 'inactive'
            )
            students.append(student)
        
        return students

    @staticmethod
    def register_student_unit(admission_number, unit_code, db):
        """Register a student for a unit."""
        # Fetch student_id based on admission_number
        student_query = "SELECT id FROM student_details WHERE admission_number = %s"
        student_result = fetch_one(db, student_query, (admission_number,))
        student_id = student_result['id'] if student_result else None

        # Fetch unit_id based on unit_code
        unit_query = "SELECT id FROM units WHERE unit_code = %s"
        unit_result = fetch_one(db, unit_query, (unit_code,))
        unit_id = unit_result['id'] if unit_result else None

        if student_id and unit_id:
            # Insert into student_unit_registrations
            register_query = """
            INSERT INTO student_unit_registrations (student_id, unit_id)
            VALUES (%s, %s)
            """
            execute_query(db, register_query, (student_id, unit_id))
            return True  # Registration successful
        else:
            return False  # Error: Invalid admission number or unit code
    
    @staticmethod
    def get_student_attendance_by_id(student, db):
            if db is None:
                raise ValueError("Database connection is None")  # Ensure db is valid

            # Ensure student is a Student object and has an 'id' attribute
            if not isinstance(student, Student) or not hasattr(student, 'id'):
                raise AttributeError("Student object has no 'id' attribute.")
            
            query = """
            SELECT a.class_date, a.hours_attended, a.total_hours, a.attendance_status
            FROM attendance a
            JOIN units u ON a.unit_id = u.id
            WHERE a.student_id = %s;
            """
            
            results = fetch_all(db, query, (student.id,))
            
            # Debug: Check the structure of results
            print("Attendance Query Results:", results)  # Ensure this returns expected data format
            
            # Ensure results are in a usable format (list of dicts or tuples)
            attendance_records = []
            if results:  # Check if results are not empty
                for result in results:
                    # Assuming fetch_all returns a list of dictionaries or tuples
                    if isinstance(result, dict):
                        attendance_records.append({
                            'class_date': result.get('class_date'),
                            'hours_attended': result.get('hours_attended'),
                            'total_hours': result.get('total_hours'),
                            'attendance_status': result.get('attendance_status')
                        })
                    else:
                        # If results are in a tuple, adjust to match the format (index-based access)
                        attendance_records.append({
                            'class_date': result[0],
                            'hours_attended': result[1],
                            'total_hours': result[2],
                            'attendance_status': result[3]
                        })
            return attendance_records
    
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
    def __init__(self, id, unit_name, unit_code, school, course, year_offered, semester_offered, status):
        self.id = id
        self.unit_name = unit_name
        self.unit_code = unit_code
        self.school = school
        self.course = course
        self.year_offered = year_offered
        self.semester_offered = semester_offered
        self.status = status

    
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
    def create_unit(unit_name, unit_code, school, course, year_offered, semester_offered, status, db):
        query = """
        INSERT INTO units (unit_name, unit_code, school, course, year_offered, semester_offered, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (unit_name, unit_code, school,course, year_offered, semester_offered, status)
        execute_query(db, query, params)

    @staticmethod
    def get_all_units(db):
        """Fetch all units from the database."""
        query = """
        SELECT id, unit_name, unit_code, school, course, year_offered, semester_offered, status
        FROM units
        """
        results = fetch_all(db, query)
        units = []
        for result in results:
            # Convert status from 0/1 to "Active"/"Inactive"
            status = "Active" if result['status'] == 0 else "Inactive"
            
            unit = Unit(
                id=result['id'],
                unit_name=result['unit_name'],
                unit_code=result['unit_code'],
                school=result['school'],
                course=result['course'],
                year_offered=result['year_offered'],
                semester_offered=result['semester_offered'],
                status=status 
            )
            units.append(unit)
        return units
    
    @staticmethod
    def get_bbit_units(db):
        """Fetch all units for the BBIT course from the database."""
        query = """
        SELECT id, unit_name, unit_code, school, course, year_offered, semester_offered, status
        FROM units
        WHERE course = %s
        """
        params = ('BBIT',)
        results = fetch_all(db, query, params)
        
        units = []
        for result in results:
            unit = Unit(
                id=result['id'],
                unit_name=result['unit_name'],
                unit_code=result['unit_code'],
                school=result['school'],
                course=result['course'],
                year_offered=result['year_offered'],
                semester_offered=result['semester_offered'],
                status=result['status']
            )
            units.append(unit)
        return units
    
    @staticmethod
    def get_compsci_units(db):
        """Fetch all units for the Computer Science course from the database."""
        query = """
        SELECT id, unit_name, unit_code, school, course, year_offered, semester_offered, status
        FROM units
        WHERE course = %s
        """
        params = ('BSC',)
        results = fetch_all(db, query, params)
        
        units = []
        for result in results:
            unit = Unit(
                id=result['id'],
                unit_name=result['unit_name'],
                unit_code=result['unit_code'],
                school=result['school'],
                course=result['course'],
                year_offered=result['year_offered'],
                semester_offered=result['semester_offered'],
                status=result['status']
            )
            units.append(unit)
        return units
    
    @staticmethod
    def get_active_units(db, status="Active"):
        """Fetch all units with a specific status from the database."""
        query = """
        SELECT id, unit_name, unit_code, school, course, year_offered, semester_offered, status
        FROM units
        WHERE status = %s
        """
        params = (status,)
        results = fetch_all(db, query, params)

        units = []
        for result in results:
            unit = Unit(
                id=result['id'],
                unit_name=result['unit_name'],
                unit_code=result['unit_code'],
                school=result['school'],
                course=result['course'],
                year_offered=result['year_offered'],
                semester_offered=result['semester_offered'],
                status=result['status'] 
            )
            units.append(unit)
    
        return units

    @staticmethod
    def fetch_registered_units_for_lecturer(lecturer_id, db):
        """
        Fetch all units registered by a lecturer.

        Args:
            lecturer_id (int): ID of the lecturer.
            db (DatabaseConnection): Database connection object.

        Returns:
            list[dict]: List of dictionaries containing unit details.
        """
        query = """
        SELECT u.id AS unit_id, u.unit_name, u.unit_code, u.school, u.course, 
            u.year_offered, u.semester_offered, u.status
        FROM lecturer_unit_registrations lur
        JOIN units u ON lur.unit_id = u.id
        WHERE lur.lecturer_id = %s
        """
        results = fetch_all(db, query, (lecturer_id,))
        return results
    
    @staticmethod
    def get_unit_by_id(unit_id, db):
        cursor = db.cursor(dictionary=True)
        query = "SELECT id, name FROM units WHERE id = %s"
        cursor.execute(query, (unit_id,))
        return cursor.fetchone()
    
    @staticmethod
    def fetch_unit_by_id_and_lecturer(unit_id, lecturer_id, db):
        """
        Fetch a unit by its ID, ensuring it belongs to the specified lecturer.
        
        :param unit_id: The ID of the unit.
        :param lecturer_id: The ID of the lecturer.
        :param db: The database connection object.
        :return: The unit if found and belongs to the lecturer, None otherwise.
        """
        cursor = None
        try:
            query = """
            SELECT units.id, units.name, units.description
            FROM units
            JOIN lecturer_unit_registrations 
                ON units.id = lecturer_unit_registrations.unit_id
            WHERE units.id = %s 
            AND lecturer_unit_registrations.lecturer_id = %s
            """
            cursor = db.cursor(dictionary=True)
            cursor.execute(query, (unit_id, lecturer_id))
            unit = cursor.fetchone()
            return unit  # Return unit if found, else None
        except Exception as e:
            print(f"Error fetching unit: {str(e)}")
            return None
        finally:
            if cursor:
                cursor.close()


    @staticmethod
    def register_unit_for_lecturer(lecturer_id, unit_id, db):
        # Validate the unit_id exists in the units table
        validate_query = "SELECT 1 FROM units WHERE id = %s"
        if not fetch_one(db, validate_query, (unit_id,)):
            raise ValueError(f"Invalid unit_id: {unit_id}")
        
        # Check if the lecturer is already registered
        check_query = """
        SELECT 1
        FROM lecturer_unit_registrations
        WHERE lecturer_id = %s AND unit_id = %s
        """
        if fetch_one(db, check_query, (lecturer_id, unit_id)):
            return False
        
        # Register the unit
        insert_query = """
        INSERT INTO lecturer_unit_registrations (lecturer_id, unit_id)
        VALUES (%s, %s)
        """
        execute_query(db, insert_query, (lecturer_id, unit_id))
        return True

    @staticmethod
    def get_sces_units_with_registration_status(lecturer_id, db):
        query = """
        SELECT u.id, u.unit_name, u.unit_code, u.school, u.course, u.year_offered, 
            u.semester_offered, 
            EXISTS (
                SELECT 1 
                FROM lecturer_unit_registrations 
                WHERE lecturer_id = %s AND unit_id = u.id
            ) AS registered
        FROM units u
        WHERE u.school = 'SCES'
        """
        results = fetch_all(db, query, (lecturer_id,))
        units = []

        for result in results:
            unit = Unit(
                id=result['id'],
                unit_name=result['unit_name'],
                unit_code=result['unit_code'],
                school=result['school'],
                course=result['course'],
                year_offered=result['year_offered'],
                semester_offered=result['semester_offered'],
                status="Registered" if result['registered'] else "Not Registered"
            )
            units.append(unit)

        return units

    @staticmethod
    def fetch_registered_units(admission_number, db):
        """
        Fetch all units a student is registered for using their admission number.

        Args:
            admission_number (str): The student's admission number.
            db (DatabaseConnection): The database connection object.

        Returns:
            list[dict]: List of dictionaries containing unit details.
        """
        query = """
        SELECT u.id, u.unit_name, u.unit_code, u.school, u.course, u.year_offered, 
               u.semester_offered, u.status
        FROM student_unit_registrations sur
        JOIN units u ON sur.unit_id = u.id
        JOIN student_details sd ON sur.student_id = sd.id
        WHERE sd.admission_number = %s
        """
        results = fetch_all(db, query, (admission_number,))
        return results
    
    @staticmethod
    def fetch_by_unit_and_student(unit_id, admission_number, db):
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT * FROM attendance
            WHERE unit_id = %s AND admission_number = %s
        """
        cursor.execute(query, (unit_id, admission_number))
        result = cursor.fetchall()
        return result

class FacultyAdmin:
    def __init__(self, user_id, school, faculty, faculty_number, faculty_status, full_name=None, mobile_number=None, email=None):
        self.user_id = user_id
        self.school = school
        self.faculty = faculty
        self.faculty_number = faculty_number
        self.faculty_status = faculty_status
        self.full_name = full_name
        self.mobile_number = mobile_number
        self.email = email

    @staticmethod
    def generate_faculty_number(db):
        """Generate a unique faculty number."""
        while True:
            random_number = random.randint(1000, 9999)
            faculty_number = f"F{random_number}"  # Prefix with 'F'

            # Check if the faculty number already exists
            query = "SELECT COUNT(*) AS count FROM faculty_admin WHERE faculty_number = %s"
            result = fetch_one(db, query, (faculty_number,))

            if result['count'] == 0:  # Unique faculty number found
                return faculty_number
            
    @staticmethod
    def create_faculty_admin(user_id, school, faculty, faculty_number, faculty_status, db):
        faculty_number = FacultyAdmin.generate_faculty_number(db)
        query = """
        INSERT INTO faculty_admin (user_id, school, faculty, faculty_number, faculty_status)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, school, faculty, faculty_number, faculty_status)
        execute_query(db, query, params)

    @staticmethod
    def find_by_user_id(user_id, db):
        """Query faculty admin details by user ID, including the faculty admin's name."""
        query = """
        SELECT u.full_name, fa.user_id, fa.school, fa.faculty, fa.faculty_number, u.mobile_number, u.email, fa.faculty_status
        FROM faculty_admin fa
        JOIN users u ON fa.user_id = u.id
        WHERE fa.user_id = %s
        """
        result = fetch_one(db, query, (user_id,))
        if result:
            return FacultyAdmin(
                user_id=result['user_id'],
                school=result['school'],
                faculty=result['faculty'],
                faculty_number=result['faculty_number'],
                full_name=result['full_name'],
                mobile_number=result['mobile_number'],
                email=result['email'],
                faculty_status=result['faculty_status']
            )
        return None
    
class Attendance:
    def __init__(self, db, attendance_id, unit_id, student_id, admission_number, class_date, hours_attended, attendance_status):
        self.db = db
        self.attendance_id = attendance_id
        self.unit_id = unit_id
        self.student_id = student_id
        self.admission_number = admission_number
        self.class_date = class_date
        self.hours_attended = hours_attended
        self.attendance_status = attendance_status

    @staticmethod
    def create_attendance(db_connection, attendance):
        """
        Inserts a new attendance record into the database.

        :param db_connection: The database connection object.
        :param attendance: An instance of the Attendance class.
        """
        query = """
        INSERT INTO attendance (unit_id, student_id, admission_number, class_date, hours_attended, total_hours, attendance_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            attendance.unit_id,
            attendance.student_id,
            attendance.admission_number,
            attendance.class_date,
            attendance.hours_attended,
            attendance.total_hours,
            attendance.attendance_status
        )

        try:
            cursor = db_connection.cursor()
            cursor.execute(query, data)
            db_connection.commit()
            print("Attendance record created successfully.")
        except Exception as e:
            print(f"Error creating attendance record: {e}")
            db_connection.rollback()
        finally:
            cursor.close()



    