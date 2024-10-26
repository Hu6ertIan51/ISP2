from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from flask_login import logout_user
from .models import User
from .db import get_db_connection 
from functools import wraps

main = Blueprint('main', __name__)

@main.route('/', endpoint='login_page')  # Specify endpoint
def login():
    return render_template('Login.html')

#registeruser
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']  # Store password as plain text
        role = request.form['role']  # Get the selected role
        dob = request.form['dob']  # Get the date of birth from form data
        mobile_number = request.form['mobile_number']  # Get mobile number from form data
        gender = request.form['gender']  # Get gender from form data

        db_connection = get_db_connection()
        
        # Check if email is already registered
        if User.find_by_email(email, db_connection):
            flash('Email is already registered!', 'error')
            return redirect(url_for('main.register'))

        # Pass all parameters to create_user method
        User.create_user(full_name, email, password, dob, mobile_number, gender, role, db_connection)
        
        flash('Registration successful!', 'success')
        return redirect(url_for('main.login_page'))

    return render_template('RegisterUser.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('main.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

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
def admin_dashboard():
    return render_template('AdminModule/AdminDashboard.html')  # Create your Admin Dashboard template

@main.route('/student_dashboard')
@login_required
def student_dashboard():
    return render_template('StudentModule/StudentDashboard.html')  # Create your Student Dashboard template

@main.route('/lecturer_dashboard')
@login_required
def lecturer_dashboard():
    return render_template('LecturerModule/LecturerDashboard.html')  # Create your Lecturer Dashboard template

@main.route('/mentor_dashboard')
@login_required
def mentor_dashboard():
    return render_template('MentorModule/MentorDashboard.html')  # Create your Mentor Dashboard template

@main.route('/success')
def success_page():
    return render_template('Message.html')


@main.route('/logout', methods=['POST'])  
def logout():
    logout_user()  # Logs out the current user
    return redirect(url_for('main.login_page'))  # Redirect to login page


