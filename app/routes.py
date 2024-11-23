from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from .models import User, Student, Lecturer, Unit, SystemAdmin, FacultyAdmin, Attendance
from .db import get_db_connection, fetch_one, fetch_all, execute_query
from functools import wraps
from datetime import datetime
from collections import defaultdict 

main = Blueprint('main', __name__)

@main.route('/', endpoint='login_page')  # Specify endpoint
def login():
    return render_template('Login.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('main.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            if current_user.role != role:  # Assuming 'role' is a property of current_user
                flash("Access denied: Unauthorized role.", "error")
                return redirect(url_for('main.login_page'))  # Redirect to a default page
            return func(*args, **kwargs)
        return wrapped_function
    return decorator


@main.route('/login', methods=['GET', 'POST'])
def login_user_view():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Get database connection
        db_connection = get_db_connection()
        
        # Find the user by email
        user = User.find_by_email(email, db_connection)
        print("Fetched user:", user)  # Debugging line

        # Check if user exists and password is correct
        if user:
            # This will use the check_password method in User class
            if user.check_password(password):  
                login_user(user)
                # Redirect based on user role
                if user.role == '0':  # Admin
                    return redirect(url_for('main.admin_dashboard'))
                elif user.role == '1':  # Student
                    return redirect(url_for('main.student_dashboard'))
                elif user.role == '2':  # Lecturer
                    return redirect(url_for('main.lecturer_dashboard'))
                elif user.role == '3':  # Mentor
                    return redirect(url_for('main.mentor_dashboard'))
                elif user.role == '4':  # Faculty Admin
                    return redirect(url_for('main.fadmindashboard'))
            else:
                print("Incorrect password")  # Log incorrect password
        else:
            print("User not found")  # Log if user is not found

        flash('Invalid email or password', 'error')
        return render_template('Login.html', email=email)  # Retain email on failed login

    return render_template('Login.html')

@main.route('/admin_dashboard')
@login_required
@role_required('0')  # Admin role
def admin_dashboard():
    user_id = current_user.id  # Get the logged-in user's ID
    db_connection = get_db_connection()

    # Fetch student details from the database
    admin_details = SystemAdmin.find_by_user_id(user_id, db_connection)

    # Handle case where student details are not found
    if admin_details is None:
        flash('Admin details not found.', 'error')
        return redirect(url_for('main.login_user_view'))  # Redirect to a safe page

    # Convert academic_status to an integer if necessary, then map to "active" or "inactive"
    admin_status = "Active" if int(admin_details.admin_status) == 0 else "Inactive"
    admin_details.admin_status = admin_status

    return render_template('AdminModule/AdminDashboard.html', admin=admin_details)

@main.route('/register', methods=['GET', 'POST'])
@login_required
@role_required('0')  # Admin role
def register():
    if request.method == 'POST':
        # Capture user details from the form
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        dob = request.form['dob']
        mobile_number = request.form['mobile_number']
        gender = request.form['gender']
        role = request.form['role']

        print(f"Registering user: {full_name}, Email: {email}, Role: {role}")

        db_connection = get_db_connection()

        # Check if email is already registered
        if User.find_by_email(email, db_connection):
            flash('Email is already registered!', 'error')
            print('Email is already registered!')
            return redirect(url_for('main.register'))  # Added return here to stop further execution
        
        # Create user
        try:
            User.create_user(full_name, email, password, dob, mobile_number, gender, role, db_connection)

            # Find the newly created user's ID
            user = User.find_by_email(email, db_connection)  # Get the user to retrieve their ID

            # Redirect based on role after user creation
            if role == '1':  # Assuming role '1' indicates a student
                flash('Registration successful! Please complete your student registration.', 'success')
                print('Registration successful! Please complete your student registration.')
                return redirect(url_for('main.register_student', user_id=user.id))  # Pass user_id as query parameter
            
            elif role == '0':  # Admin
                flash('Registration successful! Welcome Admin.', 'success')
                print('Registration successful! Welcome Admin.')
                return redirect(url_for('main.admin_registration', user_id=user.id))  # Update with actual admin dashboard route
            
            elif role == '2':  # Lecturer
                flash('Registration successful! Welcome Lecturer.', 'success')
                print('Registration successful! Welcome Lecturer.')
                return redirect(url_for('main.register_lecturer', user_id=user.id))  # Update with actual lecturer dashboard route
            
            elif role == '3':  # Mentor
                flash('Registration successful! Welcome Mentor.', 'success')
                print('Registration successful! Welcome Mentor.')
                return redirect(url_for('main.mentor_dashboard'))  # Update with actual mentor dashboard route
            
            elif role == '4':  # Faculty Admin
                flash('Registration successful! Welcome Faculty Admin.', 'success')
                print('Registration successful! Welcome Faculty Admin.')
                return redirect(url_for('main.fadmin_registration', user_id=user.id))  # Update with actual faculty admin dashboard route
            
            else:
                flash('Registration successful!', 'success')
                return redirect(url_for('main.login_user_view'))  # Fallback to login if role is unknown
            
        except Exception as e:
            flash(f"An error occurred while creating the user: {str(e)}", "error")
            print(f"An error occurred while creating the user: {str(e)}")
            return redirect(url_for('main.register'))

    return render_template('AdminModule/RegisterUser.html')

@main.route('/register_unit', methods=['GET', 'POST'])
@login_required
@role_required('0')  # Admin role
def register_unit():
    if request.method == 'POST':
        unit_name = request.form['unit_name']
        unit_code = request.form['unit_code']
        school = request.form['school']
        course = request.form['course']
        year_offered = request.form['year_offered']
        semester_offered = request.form['semester_offered']
        status = request.form['status']
        
        # Get database connection
        db_connection = get_db_connection()
        
        # Generate a unique unit code
        unit_code = Unit.generate_unit_code(unit_name, course, year_offered, semester_offered, db_connection)

        # Create the unit in the database with the generated unit_code
        Unit.create_unit(unit_name, unit_code, school, course, year_offered, semester_offered, status, db_connection)   
        
        flash('Unit registered successfully!', 'success')
        return redirect(url_for('main.admin_dashboard')) 

    return render_template('AdminModule/RegisterUnit.html')

@main.route('/generate_unit_code', methods=['POST'])
def generate_unit_code():
    data = request.get_json()
    unit_name = data.get('unit_name')
    course = data.get('course')
    year_offered = data.get('year_offered')
    semester_offered = data.get('semester_offered')
    
    # Get database connection
    db_connection = get_db_connection()
    
    # Generate the unit code
    unit_code = Unit.generate_unit_code(unit_name, course, year_offered, semester_offered, db_connection)
    
    return jsonify({"unit_code": unit_code})

@main.route('/register_student', methods=['GET', 'POST'])
@login_required
@role_required('0')
def register_student():
    db_connection = get_db_connection()
    
    # Handle GET request
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            flash("User ID is required to register a student.", "error")
            print("User ID is required to register a student.")
            return redirect(url_for('main.login_user_view'))
        
        admission_number = Student.generate_admission_number(db_connection)
        
        return render_template(
            '/AdminModule/StudentRegistration.html',
            user_id=user_id,
            admission_number=admission_number
        )

    elif request.method == 'POST':
        # Retrieve form data
        user_id = request.form.get('user_id')
        school = request.form['school']
        course = request.form['course']
        admission_number = request.form['admission_number']
        current_year = request.form['current_year']
        year_intake = request.form['year_intake']
        international = request.form['international']
        academic_status = request.form['academic_status']

        try:
            # Convert user_id to integer
            user_id = int(user_id)

            # Format the year_intake to "Month-Year"
            formatted_year_intake = datetime.strptime(year_intake, "%Y-%m").strftime("%B-%Y")

            # Save student record
            Student.create_student(
                user_id, school, course, admission_number, current_year,
                formatted_year_intake, international, academic_status, db_connection
            )
            flash('Student registration successful!', 'success')
            print('Student registration successful!')
            return redirect(url_for('main.login_user_view'))
        
        except ValueError as ve:
            flash(f"User ID error: {str(ve)}", "error")
            print(f"User ID error: {str(ve)}")
            return redirect(url_for('main.register_student'))
        
        except Exception as e:
            flash(f"An error occurred while registering the student: {str(e)}", "error")
            print(f"An error occurred while registering the student: {str(e)}")
            return redirect(url_for('main.success_page'))

@main.route('/admin_registration', methods=['GET', 'POST'])
@login_required
@role_required('0')
def admin_registration():
    db_connection = get_db_connection()

    # Handle GET request
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            flash("User ID is required to register a System admin.", "error")
            print("User ID is required to register a System admin.")
            return redirect(url_for('main.login_user_view'))
        
        staff_number = SystemAdmin.generate_staff_number(db_connection)
        
        return render_template(
            '/AdminModule/AdminRegistration.html',
            user_id=user_id,
            staff_number=staff_number
        )

    elif request.method == 'POST':
        # Retrieve form data
        user_id = request.form.get('user_id')
        staff_number = request.form['staff_number']
        year_registered = request.form['year_registered']
        admin_status = request.form['admin_status']

        try:
            # Convert user_id to integer
            user_id = int(user_id)

            # Format the year_intake to "Month-Year"
            formatted_year_registration = datetime.strptime(year_registered, "%Y-%m").strftime("%B-%Y")

            # Save student record
            SystemAdmin.create_system_admin(
                user_id, staff_number, formatted_year_registration, admin_status, db_connection
            )  
            flash('Admin registration successful!', 'success')
            print('Admin registration successful!')
            return redirect(url_for('main.login_user_view'))
        
        except ValueError as ve:
            flash(f"User ID error: {str(ve)}", "error")
            print(f"User ID error: {str(ve)}")
            return redirect(url_for('main.admin_registration'))
        
        except Exception as e:
            flash(f"An error occurred while registering the admin: {str(e)}", "error")
            print(f"An error occurred while registering the admin: {str(e)}")
            return redirect(url_for('main.success_page'))
        
    return render_template('AdminModule/AdminRegistration.html')    

@main.route('/fadmin_registration', methods=['GET', 'POST'])
#@login_required
#@role_required('0')
def fadmin_registration():
    db_connection = get_db_connection()

    # Handle GET request
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            flash("User ID is required to register a Faculty Admin.", "error")
            print("User ID is required to register a Faculty Admin.")
            return redirect(url_for('main.login_user_view'))
    
        # Generate a unique faculty number once, during GET
        faculty_number = FacultyAdmin.generate_faculty_number(db_connection)
        
        return render_template(
            '/AdminModule/FAdminRegistration.html',
            user_id=user_id,
            faculty_number=faculty_number
        )

    elif request.method == 'POST':
        # Retrieve form data
        user_id = request.form.get('user_id')
        school = request.form['school']
        faculty = request.form['faculty']
        faculty_number = request.form['faculty_number']
        faculty_status = request.form['faculty_status']

        try:
            # Convert user_id to integer
            user_id = int(user_id)


            # Save faculty admin record
            FacultyAdmin.create_faculty_admin(
                user_id, school, faculty, faculty_number, faculty_status, db_connection
            )
            flash('Faculty Admin registration successful!', 'success')
            print('Faculty Admin registration successful!')
            return redirect(url_for('main.login_user_view'))
        
        except ValueError as ve:
            flash(f"User ID error: {str(ve)}", "error")
            print(f"User ID error: {str(ve)}")
            return redirect(url_for('main.fadmin_registration'))
        
        except Exception as e:
            flash(f"An error occurred while registering the Faculty Admin: {str(e)}", "error")
            print(f"An error occurred while registering the Faculty Admin: {str(e)}")
            return redirect(url_for('main.login_user_view'))

    
    return render_template('/AdminModule/FAdminRegistration.html')


@main.route('/student_dashboard', methods=['GET'])
@login_required
@role_required('1')  # Assuming '1' is the student role
def student_dashboard():
    user_id = current_user.id  # Get the logged-in user's ID
    db_connection = get_db_connection()

    # Fetch student details from the database
    student_details = Student.find_by_user_id(user_id, db_connection)

    # Handle case where student details are not found
    if student_details is None:
        flash('Student details not found.', 'error')
        return redirect(url_for('main.login_user_view'))  # Redirect to a safe page

    # Convert academic_status to an integer if necessary, then map to "active" or "inactive"
    academic_status = "Active" if int(student_details.academic_status) == 0 else "Inactive"
    student_details.academic_status = academic_status

    return render_template('StudentModule/StudentDashboard.html', student=student_details)

@main.route('/register_student_unit', methods=['GET', 'POST'])
@login_required
@role_required('1')  # Student role
def register_student_unit():
    db = get_db_connection()

    if request.method == 'POST':
        # Handle form submission
        admission_number = request.form.get('admission_number')
        unit_code = request.form.get('unit_code')

        # Call the register_student_unit method from the Student model to register the unit
        registration_successful = Student.register_student_unit(admission_number, unit_code, db)

        if registration_successful:
            flash("Successfully registered for the unit.", "success")
            print("Successfully registered for the unit.")
        else:
            flash("Error: Invalid admission number or unit code.", "error")
            print("Error: Invalid admission number or unit code.")

        # Redirect to a relevant page after successful registration (e.g., available units)
        return redirect(url_for('main.available_units'))

    # For GET request, fetch the student's details and available units
    user_id = current_user.id  # Get the current user's ID from Flask-Login
    student = Student.find_by_user_id(user_id, db)

    if not student:
        flash("No student details found.", "error")
        return redirect(url_for('main.index'))  # Redirect to the index page if no student is found

    # Fetch available units from the database (unit_code and unit_name)
    units_query = "SELECT unit_code, unit_name FROM units"
    units = fetch_all(db, units_query)

    # Render the template and pass the student and units data
    return render_template('register_student_unit.html', student=student, units=units)

@main.route('/student/attendance', methods=['GET'])
@main.route('/student/attendance/<int:unit_id>', methods=['GET'])  # Accept unit_id from URL
@login_required
@role_required('1')  # Student role
def student_attendance(unit_id=None):
    db = get_db_connection()
    try:
        # Fetch the student record using current_user.id
        query_student = "SELECT * FROM student_details WHERE user_id = %s;"
        student_result = fetch_one(db, query_student, (current_user.id,))

        if not student_result:
            flash("Student record not found.", "error")
            return redirect(url_for('main.index'))

        # If a unit_id is provided, fetch only the attendance for that unit
        if unit_id:
            query_attendance = """
            SELECT 
                a.class_date, 
                a.hours_attended, 
                a.total_hours, 
                a.attendance_status, 
                a.absenteeism_percentage,
                u.unit_name -- Include unit name
            FROM 
                attendance a
            JOIN 
                units u ON a.unit_id = u.id
            WHERE 
                a.student_id = %s AND a.unit_id = %s
            ORDER BY 
                a.class_date;
            """
            attendance_results = fetch_all(db, query_attendance, (student_result['id'], unit_id))
        else:
            # If no unit_id is provided, fetch all attendance records for the student
            query_attendance = """
            SELECT 
                a.class_date, 
                a.hours_attended, 
                a.total_hours, 
                a.attendance_status, 
                a.absenteeism_percentage,
                u.unit_name -- Include unit name
            FROM 
                attendance a
            JOIN 
                units u ON a.unit_id = u.id
            WHERE 
                a.student_id = %s
            ORDER BY 
                u.unit_name, a.class_date;
            """
            attendance_results = fetch_all(db, query_attendance, (student_result['id'],))

        # Group attendance records by unit
        attendance_by_unit = defaultdict(list)
        for record in attendance_results:
            unit_name = record['unit_name']
            attendance_by_unit[unit_name].append({
                'class_date': record['class_date'],
                'hours_attended': record['hours_attended'],
                'total_hours': record['total_hours'],
                'attendance_status': record['attendance_status'],
                'absenteeism_percentage': record['absenteeism_percentage'],
            })

        # Sort attendance records by class_date (latest first) to show the most recent absenteeism
        for unit in attendance_by_unit:
            attendance_by_unit[unit].sort(key=lambda x: x['class_date'], reverse=True)

        # Convert to a regular dictionary for easier rendering
        attendance_by_unit = dict(attendance_by_unit)

        # Render the attendance page
        return render_template(
            'StudentModule/AttendanceRecords.html',
            attendance_by_unit=attendance_by_unit,  # Pass grouped data
            student=student_result  # Pass the student details to the template
        )

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('main.student_dashboard'))


@main.route('/available_units', methods=['GET', 'POST'])
@login_required
@role_required('1')
def available_units():
    db = get_db_connection()
    
    # Handle POST request for unit registration
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        unit_id = request.form.get('unit_id')
        admission_number = request.form.get('admission_number')
        unit_name = request.form.get('unit_name')
        unit_code = request.form.get('unit_code')
        registration_status = request.form.get('registration_status')
        
        
        # Fetch the correct student_id if not directly provided
        cursor = db.cursor()
        cursor.execute("SELECT id FROM student_details WHERE user_id = %s", (current_user.id,))
        result = cursor.fetchone()
        if result:
            student_id = result[0]
        else:
            flash('Student details not found. Please contact support.', 'error')
            return redirect(url_for('main.available_units'))
        
        # Validate input
        if not (student_id and unit_id and admission_number and unit_name and unit_code):
            flash('All fields are required.', 'error')
            return redirect(url_for('main.available_units'))
        
        # Check if the student has already registered for this unit
        cursor.execute("""
            SELECT id FROM student_unit_registrations 
            WHERE student_id = %s AND unit_id = %s
        """, (student_id, unit_id))
        existing_registration = cursor.fetchone()
        
        if existing_registration:
            flash('You have already registered for this unit.', 'error')
            return redirect(url_for('main.available_units'))
        
        try:
            # Insert registration details into the database
            cursor.execute("""
                INSERT INTO student_unit_registrations (student_id, unit_id, admission_number, unit_name, unit_code, registration_status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_id, unit_id, admission_number, unit_name, unit_code, registration_status))
            db.commit()
            flash('Unit registered successfully!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error registering unit: {str(e)}', 'error')
        finally:
            cursor.close()
    
    # Fetch student details and active units for GET requests
    student = Student.find_by_student_id(db, current_user.id)
    units = Student.get_units_for_student(db, current_user.id)
    
    return render_template('StudentModule/UnitRegistration.html', student=student, units=units) 


@main.route('/inprogressunits', methods=['GET', 'POST'])
@login_required
@role_required('1')  # Ensure the user is a student
def inprogressunits():
    db = get_db_connection()
    try:
        # Fetch the student details for the logged-in user
        student = Student.find_by_user_id(current_user.id, db)
        if not student:
            flash("Student record not found.", 'error')
            return redirect(url_for('main.student_dashboard'))

        # Fetch the registered units using the student's admission_number
        units = Unit.fetch_registered_units(student.admission_number, db)
        return render_template('StudentModule/InProgressUnits.html', units=units)
    except Exception as e:
        flash(f"Error fetching units: {str(e)}", 'error')
        print(f"Error fetching units: {str(e)}")
        return redirect(url_for('main.student_dashboard'))

@main.route('/attendance/<unit_id>', methods=['GET', 'POST'])
@login_required
@role_required('1')  # Ensure the user is a student
def attendance(unit_id):
    db = get_db_connection()  # Step 1: Establish a database connection

    try:
        # Step 2: Fetch the student details for the logged-in user
        student = Student.find_by_student_id(current_user.id, db)
        if not student:
            flash("Student record not found.", 'error')
            return redirect(url_for('main.student_dashboard'))

        # Step 3: Fetch the unit based on unit_id
        unit_query = """SELECT * FROM units WHERE id = %s"""
        cursor = db.cursor(dictionary=True)
        cursor.execute(unit_query, (unit_id,))
        unit = cursor.fetchone()  # Fetch the unit details

        # If unit is not found, flash an error and redirect
        if not unit:
            flash("Unit not found.", 'error')
            return redirect(url_for('main.inprogressunits'))

        # Step 4: Fetch attendance for the student in the selected unit
        attendance_query = """SELECT * FROM attendance WHERE unit_id = %s AND student_id = %s"""
        cursor.execute(attendance_query, (unit_id, student.id))  # Use student.id
        attendance_records = cursor.fetchall()  # Fetch all attendance records

        cursor.close()  # Close the cursor to free up resources

        # Step 5: If no attendance records found, flash a warning
        if not attendance_records:
            flash("No attendance records found for this unit.", 'warning')

        # Render the attendance records page with the fetched data
        return render_template('StudentModule/AttendanceRecords.html', unit=unit, attendance_records=attendance_records)

    except Exception as e:
        # Catch any exceptions and display an error message
        flash(f"Error fetching attendance: {str(e)}", 'error')
        print(f"Error fetching attendance: {str(e)}")  # Log the error for debugging
        return redirect(url_for('main.student_dashboard'))

@main.route('/manageunitslec/<int:unit_id>', methods=['GET', 'POST'])
@login_required
@role_required('2')  # Lecturer role
def manageunitslec(unit_id):

    db = get_db_connection()
    lecturer_id = current_user.id

    # Validate if lecturer has access to the unit
    query = """
    SELECT 1
    FROM lecturer_unit_registrations
    WHERE lecturer_id = %s AND unit_id = %s
    """
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, (lecturer_id, unit_id))
    if not cursor.fetchone():
        flash("Unauthorized access to this unit.", "error")
        return redirect(url_for('main.lecturer_dashboard'))

    # Fetch students for this specific unit
    query_students = """
    SELECT s.admission_number, s.course, su.student_id AS id
    FROM student_details s
    JOIN student_unit_registrations su ON su.student_id = s.id
    WHERE su.unit_id = %s
    """
    cursor.execute(query_students, (unit_id,))
    students = cursor.fetchall()
    cursor.close()

    return render_template('LecturerModule/LecManageUnits.html', students=students, unit_id=unit_id)

@main.route('/attendance', methods=['POST'])
@login_required
@role_required('2')  
def record_attendance():
    db = get_db_connection()
    lecturer_id = current_user.id

    # Get form data
    admission_number = request.form.get('admission_number')  # Adjusting to fetch admission number
    unit_id = request.form.get('unit_id')
    class_date = request.form.get('class_date')
    hours_attended = int(request.form.get('hours_attended'))
    total_hours = int(request.form.get('total_hours'))
    attendance_status = request.form.get('attendance_status')

    # Validate lecturer's access to the unit
    query_validate_lecturer = """
    SELECT 1
    FROM lecturer_unit_registrations
    WHERE lecturer_id = %s AND unit_id = %s
    """
    cursor = db.cursor(dictionary=True)
    cursor.execute(query_validate_lecturer, (lecturer_id, unit_id))
    if not cursor.fetchone():
        flash("Unauthorized action for this unit.", "error")
        return redirect(url_for('main.lecturer_dashboard'))

    # Fetch the student_id using the admission_number and unit_id
    query_get_student_id = """
    SELECT student_id
    FROM student_unit_registrations
    WHERE admission_number = %s AND unit_id = %s
    """
    cursor.execute(query_get_student_id, (admission_number, unit_id))
    student = cursor.fetchone()

    if not student:
        flash("No student found with the provided admission number for this unit.", "error")
        return redirect(url_for('main.manageunitslec', unit_id=unit_id))

    student_id = student['student_id']

    # Check if the attendance for the same date, student, and unit already exists
    query_check_duplicate = """
    SELECT 1 
    FROM attendance
    WHERE student_id = %s AND unit_id = %s AND class_date = %s
    """
    cursor.execute(query_check_duplicate, (student_id, unit_id, class_date))
    if cursor.fetchone():
        flash("Attendance for this date has already been recorded.", "error")
        cursor.close()
        return redirect(url_for('main.manageunitslec', student_id=student_id, unit_id=unit_id))

    # Insert attendance record into the database
    query_insert = """
    INSERT INTO attendance (student_id, unit_id, class_date, hours_attended, total_hours, attendance_status)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query_insert, (student_id, unit_id, class_date, hours_attended, total_hours, attendance_status))
        
        # Update cumulative total_updated_hours
        query_update_hours = """
        UPDATE attendance
        SET total_updated_hours = (
            SELECT COALESCE(SUM(hours_attended), 0)
            FROM attendance
            WHERE student_id = %s AND unit_id = %s
        )
        WHERE student_id = %s AND unit_id = %s
        """
        cursor.execute(query_update_hours, (student_id, unit_id, student_id, unit_id))

        db.commit()
        flash("Attendance recorded successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error recording attendance: {str(e)}", "error")
    finally:
        cursor.close()

    return redirect(url_for('main.manageunitslec', student_id=student_id, unit_id=unit_id))

@main.route('/editattendance/<int:unit_id>', methods=['GET', 'POST'])
@login_required
@role_required('2')  # Lecturer role
def editattendance(unit_id):
    db = get_db_connection()
    lecturer_id = current_user.id
    cursor = None  # Initialize cursor to avoid UnboundLocalError

    unit = None  # Initialize unit variable to prevent UnboundLocalError

    if request.method == 'GET':
        # Fetch the selected unit for the current lecturer
        try:
            # Directly fetch the unit and check if it belongs to the current lecturer
            query = """
            SELECT units.id, units.unit_name 
            FROM units
            JOIN lecturer_unit_registrations 
                ON units.id = lecturer_unit_registrations.unit_id
            WHERE units.id = %s 
            AND lecturer_unit_registrations.lecturer_id = %s
            """
            cursor = db.cursor(dictionary=True)
            cursor.execute(query, (unit_id, lecturer_id))
            unit = cursor.fetchone()

            if not unit:
                flash("Unit not found or you are not authorized to access it.", "error")
                return redirect(url_for('main.viewattendanceunits'))  # Adjust redirect as needed

            # Fetch attendance records for the specific unit and its students
            attendance_query = """
            SELECT 
                attendance.id, 
                student_details.admission_number, 
                student_details.user_id AS student_id, 
                attendance.unit_id,
                attendance.class_date, 
                attendance.hours_attended, 
                attendance.total_hours,
                attendance.attendance_status
            FROM 
                attendance
            JOIN 
                student_details ON attendance.student_id = student_details.id
            WHERE 
                attendance.unit_id = %s
            """

            cursor.execute(attendance_query, (unit_id,))
            attendance_records = cursor.fetchall()

        except Exception as e:
            flash(f"An error occurred while fetching data: {str(e)}", "error")
            attendance_records = []

        finally:
            if cursor:
                cursor.close()

        # Ensure that unit is always passed to the template
        return render_template(
            'LecturerModule/ManageAttendance.html',
            unit=unit,
            attendance_records=attendance_records,
        )

@main.route('/updateattendance', methods=['POST'])
@login_required
@role_required('2')
def updateattendance():
    db = get_db_connection()
    lecturer_id = current_user.id

    # Debugging: Print form data
    print("Form Data:", request.form)

    try:
        attendance_id = request.form.get('attendance_id')
        student_id = request.form.get('student_id')
        unit_id = request.form.get('unit_id')  # Ensure unit_id is in the form
        class_date = request.form.get('class_date')
        hours_attended = int(request.form.get('hours_attended', 0))  # Default to 0 if missing
        attendance_status = request.form.get('attendance_status')

        # Validate required fields
        if not attendance_id or not student_id or not unit_id or not attendance_status:
            flash("Missing required fields. Please check your input.", "error")
            return redirect(url_for('main.lecturer_dashboard'))

        # Validate lecturer's access
        query_validate_lecturer = """
        SELECT 1
        FROM lecturer_unit_registrations
        WHERE lecturer_id = %s AND unit_id = %s
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute(query_validate_lecturer, (lecturer_id, unit_id))
        if not cursor.fetchone():
            flash("Unauthorized action for this unit.", "error")
            return redirect(url_for('main.lecturer_dashboard'))

        # Update the attendance record
        query_update = """
        UPDATE attendance
        SET hours_attended = %s, attendance_status = %s
        WHERE id = %s
        """
        cursor.execute(query_update, (hours_attended, attendance_status, attendance_id))
        db.commit()

        flash("Attendance record updated successfully!", "success")
        return redirect(url_for('main.editattendance', unit_id=unit_id))
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('main.lecturer_dashboard'))

#grades       
@main.route('/save_grades', methods=['POST'])
@login_required
@role_required('2')  # Assuming only lecturers (role ID 2) can submit grades
def save_grades():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # Retrieve data from the form
        unit_id = request.form.get('unit_id')
        student_id = request.form.get('student_id')
        cat1_mark = int(request.form.get('cat1_marks', 0))
        cat2_mark = int(request.form.get('cat2_marks', 0))
        assignment1_mark = int(request.form.get('ass1_marks', 0))
        assignment2_mark = int(request.form.get('ass2_marks', 0))
        exam_mark = int(request.form.get('exam_marks', 0))

        # Validate marks
        if any(mark < 0 or mark > 100 for mark in [cat1_mark, cat2_mark, assignment1_mark, assignment2_mark, exam_mark]):
            flash("Marks must be between 0 and 100.", "error")
            return redirect(url_for('main.lecturer_dashboard'))

        # Ensure CATs and Assignments do not exceed 50
        total_cats_and_assignments = cat1_mark + cat2_mark + assignment1_mark + assignment2_mark
        if total_cats_and_assignments > 50:
            flash("Total CATs and Assignments cannot exceed 50 marks.", "error")
            return redirect(url_for('main.lecturer_dashboard'))

        # Ensure total grade does not exceed 100
        total_grade = total_cats_and_assignments + exam_mark
        if total_grade > 100:
            flash("Total grade cannot exceed 100 marks.", "error")
            return redirect(url_for('main.lecturer_dashboard'))

        # Check if the grades exist for the student and unit
        existing_grades_query = """
            SELECT * FROM grades WHERE student_id = %s AND unit_id = %s
        """
        cursor.execute(existing_grades_query, (student_id, unit_id))
        existing_grades = cursor.fetchone()

        if existing_grades:
            # Update grades
            update_query = """
                UPDATE grades SET cat1_mark = %s, cat2_mark = %s, assignment1_mark = %s,
                assignment2_mark = %s, exam_mark = %s WHERE student_id = %s AND unit_id = %s
            """
            cursor.execute(update_query, (cat1_mark, cat2_mark, assignment1_mark, assignment2_mark, exam_mark, total_grade, student_id, unit_id))
            flash("Grades updated successfully.", "success")
        else:
            # Insert grades 
            insert_query = """
                INSERT INTO grades (student_id, unit_id, cat1_mark, cat2_mark, assignment1_mark, 
                assignment2_mark, exam_mark, total_grade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (student_id, unit_id, cat1_mark, cat2_mark, assignment1_mark, assignment2_mark, exam_mark, total_grade))
            flash("Grades saved successfully.", "success")

        db.commit()
    except Exception as e:
        db.rollback()
        flash(f"Error saving grades: {str(e)}", "error")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('main.lecturer_dashboard'))


@main.route('/register_lecturer', methods=['GET', 'POST'])
@login_required
@role_required('0') 
def register_lecturer():
    db_connection = get_db_connection()

    # Handle GET request
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            flash("User ID is required to register a lecturer.", "error")
            print("User ID is required to register a lecturer.")
            return redirect(url_for('main.login_user_view'))

        lecturer_number = Lecturer.generate_lecturer_number(db_connection)

        # Optionally, fetch lecturer details if needed (this is just an example)
        lecturer = Lecturer.find_by_user_id(user_id, db_connection)

        return render_template(
            '/AdminModule/RegisterLecturer.html',
            user_id=user_id,
            lecturer_number=lecturer_number,
            lecturer=lecturer  # Pass the lecturer object to the template
        )

    elif request.method == 'POST':
        # Retrieve form data
        user_id = request.form.get('user_id')
        school = request.form['school']
        lecturer_number = request.form['lecturer_number']
        year_intake = request.form['year_intake']
        lecturer_status = request.form['lecturer_status']

        try:
            # Convert user_id to integer
            user_id = int(user_id)

            # Format the year_intake to "Month-Year"
            formatted_year_intake = datetime.strptime(year_intake, "%Y-%m").strftime("%B-%Y")

            # Save lecturer record
            Lecturer.create_lecturer(
                user_id, school, lecturer_number, formatted_year_intake, lecturer_status, db_connection
            )
            flash('Lecturer registration successful!', 'success')
            print('Lecturer registration successful!')
            return redirect(url_for('main.login_user_view'))

        except ValueError as ve:
            flash(f"User ID error: {str(ve)}", "error")
            print(f"User ID error: {str(ve)}")
            return redirect(url_for('main.register_lecturer'))

        except Exception as e:
            flash(f"An error occurred while registering the lecturer: {str(e)}", "error")
            print(f"An error occurred while registering the lecturer: {str(e)}")
            return redirect(url_for('main.success_page'))


@main.route('/lecturer_dashboard')
@login_required
@role_required('2')  # Lecturer role
def lecturer_dashboard():
    user_id = current_user.id  # Get the logged-in user's ID
    db_connection = get_db_connection()

    # Fetch lecturer details from the database
    lecturer_details = Lecturer.find_by_user_id(user_id, db_connection)

    # Handle case where lecturer details are not found
    if lecturer_details is None:
        flash('Lecturer details not found.', 'error')
        return redirect(url_for('main.login_user_view'))  # Redirect to a safe page

    # Convert academic_status to an integer if necessary, then map to "active" or "inactive"
    lecturer_status = "Active" if int(lecturer_details.lecturer_status) == 0 else "Inactive"
    lecturer_details.lecturer_status = lecturer_status

    # Pass the lecturer details to the template
    return render_template(
        'LecturerModule/LecturerDashboard.html',
        lecturer=lecturer_details  # Pass the lecturer object to the template
    )

@main.route('/viewattendanceunits', methods=['GET', 'POST'])
@login_required
@role_required('2')  
def viewattendanceunits():
    db = get_db_connection()
    lecturer_id = current_user.id
    units = Unit.fetch_registered_units_for_lecturer(lecturer_id, db)
    return render_template('LecturerModule/ViewAttendanceUnits.html', units=units)  


@main.route('/mentor_dashboard')
@login_required
@role_required('3')  # Mentor role
def mentor_dashboard():
    return render_template('MentorModule/MentorDashboard.html')

@main.route('/manageusers')
@login_required
@role_required('0')
def manageusers():
    return render_template('AdminModule/ManageUser.html')

@main.route('/managecourseinfo')
@login_required
@role_required('0')
def managecourseinfo():
    return render_template('AdminModule/ManageCourse.html')

@main.route('/fadmindashboard')
@login_required
@role_required('4')
def fadmindashboard():
    
    user_id = current_user.id  # Get the logged-in user's ID
    db_connection = get_db_connection()

    # Fetch student details from the database
    fadmin_details = FacultyAdmin.find_by_user_id(user_id, db_connection)

    # Handle case where student details are not found
    if fadmin_details is None:
        flash('Faculty Admin details not found.', 'error')
        return redirect(url_for('main.login_user_view'))  # Redirect to a safe page

    # Convert academic_status to an integer if necessary, then map to "active" or "inactive"
    faculty_status = "Active" if int(fadmin_details.faculty_status) == 0 else "Inactive"
    fadmin_details.faculty_status = faculty_status
    
    return render_template('FacultyAdmin/FAdminDashboard.html', fadmin=fadmin_details)

@main.route('/famanagecourse', methods=['GET', 'POST'])
@login_required
@role_required('4')
def famanagecourse():
    return render_template('FacultyAdmin/FAdminManageCourse.html')

@main.route('/faunitdashboard', methods=['GET', 'POST'])
@login_required
@role_required('4')
def faunitdashboard():
    return render_template('FacultyAdmin/UnitDashboard.html')

@main.route('/faviewcourse', methods = ['GET', 'POST'])
@login_required
@role_required('4')
def faviewcourse():
    return render_template('FacultyAdmin/ViewCourseUnits.html')

@main.route('/bbitunits', methods=['GET', 'POST'])
@login_required
@role_required('4')
def bbitunits():
    db = get_db_connection()
    bbit_units = Unit.get_bbit_units(db)
    return render_template('FacultyAdmin/BBIT.html', units=bbit_units)

@main.route('/compsciunits', methods=['GET', 'POST'])
@login_required
@role_required('4')
def compsciunits():
    db = get_db_connection()
    compsci_units = Unit.get_compsci_units(db)
    return render_template('FacultyAdmin/ComputerScience.html', units=compsci_units)

@main.route('/viewusers')
@login_required
@role_required('0')
def viewusers():
    return render_template('/AdminModule/ViewUsers.html')

@main.route('/viewstudents')
@login_required
@role_required('0')
def viewstudents():
    # Get database connection
    db = get_db_connection()
    # Fetch all student records
    student_list = Student.get_all_students(db)
    return render_template('/AdminModule/ViewStudents.html', students=student_list)

@main.route('/lecregunits')
@login_required
@role_required('2')  # Lecturer role
def lecregunits():
    db = get_db_connection()  # Function to connect to the database
    lecturer_id = current_user.id  # Get the current lecturer's ID

    # Fetch all units and mark those already registered
    units = Unit.get_sces_units_with_registration_status(lecturer_id, db)
    return render_template('LecturerModule/RegisterUnits.html', units=units)


@main.route('/unit_enrollment', methods=['POST'])
@login_required
@role_required('2')  # Lecturer role
def unit_enrollment():
    db = get_db_connection()
    lecturer_id = request.form.get('lecturer_id')
    unit_id = request.form.get('unit_id')

    try:
        # Try registering the unit for the lecturer
        if Unit.register_unit_for_lecturer(lecturer_id, unit_id, db):
            flash('Unit successfully registered!', 'success')
        else:
            flash('You are already registered for this unit.', 'warning')

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('main.lecregunits'))
 
@main.route('/inprogressunitslec', methods=['GET'])
@login_required 
@role_required('2')  # Lecturer role
def inprogressunitslec():
    lecturer_id = current_user.id
    db = get_db_connection()  # Replace with your actual database connection method
    
    # Fetch registered units for the lecturer
    try:
        units = Unit.fetch_registered_units_for_lecturer(lecturer_id, db)
    except Exception as e:
        flash(f"An error occurred while fetching units: {str(e)}", "error")
        units = []

    return render_template(
        'LecturerModule/InProgressUnits.html',
        units=units
    )

@main.route('/viewlecturers')
@login_required
@role_required('0')
def viewlecturers():
    # Get database connection
    db = get_db_connection()
    # Fetch all lecturer records
    lecturers = Lecturer.get_all_lecturers(db)
    return render_template('/AdminModule/ViewLecturers.html', lecturers=lecturers)

@main.route('/viewunits')
@login_required
@role_required('0')
def viewunits():
    # Get database connection
    db = get_db_connection()
    # Fetch all unit records
    units = Unit.get_all_units(db)
    return render_template('/AdminModule/ViewUnits.html', units=units)

@main.route('/post_unit/<int:unit_id>', methods=['POST'])
@login_required
@role_required('4')
def post_unit(unit_id):
    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE units SET status = %s WHERE id = %s", ('Active', unit_id))  # Ensure status is set to 'Posted'
        db.commit()
        flash('Unit posted successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error posting unit: {str(e)}', 'error')
    finally:
        cursor.close()

    return redirect(url_for('main.fadmindashboard'))  # Make sure to redirect to reload the page

@main.route('/unpost_unit/<int:unit_id>', methods=['POST'])
@login_required
@role_required('4')
def unpost_unit(unit_id):
    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE units SET status = %s WHERE id = %s", ('Inactive', unit_id))
        db.commit()
        flash('Unit unposted successfully.', 'success')
        print('Unit unposted successfully.')
    except Exception as e:
        db.rollback()
        flash(f'Error unposting unit: {str(e)}', 'error')
        print(f'Error unposting unit: {str(e)}')
    finally:
        cursor.close()

    return redirect(url_for('main.fadmindashboard'))

@main.route('/OngoingUnits')
@login_required
@role_required('4')
def OngoingUnits(): 
    # Assuming db is your database connection
    db = get_db_connection()  # Your method to get a database connection
    units = Unit.get_active_units(db)
    return render_template('FacultyAdmin/OngoingUnits.html', units=units)

@main.route('/success')
def success_page():
    return render_template('Message.html')


@main.route('/logout', methods=['POST'])  
def logout():
    logout_user()  # Logs out the current user
    return redirect(url_for('main.login_page'))  # Redirect to login page
 

 