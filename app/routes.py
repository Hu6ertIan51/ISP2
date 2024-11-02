from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from .models import User, Student
from .db import get_db_connection
from functools import wraps

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
    return render_template('AdminModule/AdminDashboard.html')

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
            return redirect(url_for('main.register'))  # Added return here to stop further execution
        
        # Create user
        try:
            User.create_user(full_name, email, password, dob, mobile_number, gender, role, db_connection)

            # Find the newly created user's ID
            user = User.find_by_email(email, db_connection)  # Get the user to retrieve their ID

            # Redirect based on role after user creation
            if role == '1':  # Assuming role '1' indicates a student
                flash('Registration successful! Please complete your student registration.', 'success')
                return redirect(url_for('main.register_student', user_id=user.id))  # Pass user_id as query parameter
            elif role == '0':  # Admin
                flash('Registration successful! Welcome Admin.', 'success')
                return redirect(url_for('main.login_user_view'))  # Update with actual admin dashboard route
            elif role == '2':  # Lecturer
                flash('Registration successful! Welcome Lecturer.', 'success')
                return redirect(url_for('main.lecturer_dashboard'))  # Update with actual lecturer dashboard route
            elif role == '3':  # Mentor
                flash('Registration successful! Welcome Mentor.', 'success')
                return redirect(url_for('main.mentor_dashboard'))  # Update with actual mentor dashboard route
            else:
                flash('Registration successful!', 'success')
                return redirect(url_for('main.login_user_view'))  # Fallback to login if role is unknown
            
        except Exception as e:
            flash(f"An error occurred while creating the user: {str(e)}", "error")
            return redirect(url_for('main.register'))

    return render_template('AdminModule/RegisterUser.html')

@main.route('/register_student', methods=['GET', 'POST'])
@login_required
@role_required('0')
def register_student():
    db_connection = get_db_connection()
    
    # Generate an admission number on the GET request and pass it to the form
    if request.method == 'GET':
        user_id = request.args.get('user_id')  # Retrieve user_id from query parameters
        if not user_id:
            flash("User ID is required to register a student.", "error")
            print("User ID is required to register a student.")
            return redirect(url_for('main.login_user_view'))  # Redirect if user_id is missing

        admission_number = Student.generate_admission_number(db_connection)
        
        return render_template(
            '/AdminModule/StudentRegistration.html',
            user_id=user_id,
            admission_number=admission_number
        )

    elif request.method == 'POST':
        # Retrieve user_id, school, and course from the form
        user_id = request.form.get('user_id')
        school = request.form['school']
        course = request.form['course']
        admission_number = request.form['admission_number']
        current_year = request.form['current_year']

        # Ensure user_id is converted to an integer
        try:
            user_id = int(user_id)
            
            # Create the student record
            Student.create_student(user_id, school, course, admission_number, current_year, db_connection)
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
        return redirect(url_for('main.index'))  # Redirect to a safe page

    return render_template('StudentModule/StudentDashboard.html', student=student_details)

@main.route('/lecturer_dashboard')
@login_required
@role_required('2')  # Lecturer role
def lecturer_dashboard():
    return render_template('LecturerModule/LecturerDashboard.html')

@main.route('/mentor_dashboard')
@login_required
@role_required('3')  # Mentor role
def mentor_dashboard():
    return render_template('MentorModule/MentorDashboard.html')

@main.route('/success')
def success_page():
    return render_template('Message.html')


@main.route('/logout', methods=['POST'])  
def logout():
    logout_user()  # Logs out the current user
    return redirect(url_for('main.login_page'))  # Redirect to login page


