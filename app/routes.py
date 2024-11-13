from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from .models import User, Student, Lecturer, Unit, SystemAdmin, FacultyAdmin
from .db import get_db_connection
from functools import wraps
from datetime import datetime

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
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('Access denied.', 'error')
                return redirect(url_for('main.login_page'))  # or a custom "access denied" page
            return f(*args, **kwargs)
        return decorated_function
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
@role_required('2')
def lecregunits():
    return render_template('LecturerModule/RegisterUnits.html')

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
        # Update the status in the database
        cursor = db.cursor()
        cursor.execute("UPDATE units SET status = %s WHERE id = %s", ('Active', unit_id))
        db.commit()
        print(f"Unit {unit_id} posted successfully.")
        flash('Unit posted successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error posting unit: {str(e)}', 'error')
        print(f'Error posting unit: {str(e)}')  
    finally:
        cursor.close()
    
    return redirect(url_for('main.fadmindashboard'))

@main.route('/OngoingUnits')
@login_required
@role_required('4')
def OngoingUnits():

    return render_template('FacultyAdmin/OngoingUnits.html')

@main.route('/success')
def success_page():
    return render_template('Message.html')


@main.route('/logout', methods=['POST'])  
def logout():
    logout_user()  # Logs out the current user
    return redirect(url_for('main.login_page'))  # Redirect to login page
 

