from flask import Flask, render_template

app = Flask(__name__)

#routes

#login route/ default page

@app.route('/')
def login():
    return render_template('Login.html')

#adminroutes

@app.route('/admindashboard')
def admin_dashboard():
    return render_template('AdminModule/AdminDashboard.html')

@app.route('/managecourse')
def manage_course():
    return render_template('AdminModule/ManageCourse.html')

@app.route('/manageuser')
def manage_user():
    return render_template('AdminModule/ManageUser.html') 

@app.route('/viewalerts')
def view_alerts():
    return render_template('AdminModule/ViewAlerts.html') 

@app.route('/viewanalytics')
def view_analytics():
    return render_template('AdminModule/ViewAnalytics.html') 

@app.route('/pendingfees')
def pending_fees():
    return render_template('AdminModule/ViewPendingFees.html') 

#lecturer routes

@app.route('/inputgrades')
def input_grades():
    return render_template('LecturerModule/InputGrades.html') 

@app.route('/lecturerdashboard')
def lecturer_dashboard():
    return render_template('LecturerModule/LecturerDashboard.html')

@app.route('/lecturerattendance')
def lecturer_attendance():
    return render_template('LecturerModule/LecturerAttendanceRecords.html')

@app.route('/registerunit')
def register_unit():
    return render_template('LecturerModule/RegisterUnits.html')

@app.route('/mentorlogin')
def mentor_login():
    return render_template('Login.html')


#Mentor Module

@app.route('/mentordashboard')
def mentor_dashboard():
    return render_template('MentorModule/MentorDashboard.html')

@app.route('/logsession')
def log_session():
    return render_template('MentorModule/LogSession.html')

#Student Module

@app.route('/studentdashboard')
def student_dashboard():
    return render_template('StudentModule/StudentDashboard.html')

@app.route('/attendancerecords')
def student_records():
    return render_template('StudentModule/AttendanceRecords.html')

@app.route('/feesbalance')
def fee_balance():
    return render_template('StudentModule/FeeBalance.html')

@app.route('/progressreport')
def progress_reportt():
    return render_template('StudentModule/Grades.html')

@app.route('/mentorinformation')
def mentor_info():
    return render_template('StudentModule/MentorInformation.html')

@app.route('/itworked')
def success():
    return render_template('Message.html')



"""
#end of routes
from flask import Flask, render_template, request, redirect, url_for, flash
import mariadb

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MariaDB
def get_db_connection():
    try:
        conn = mariadb.connect(
            user='root',  
            password='',  
            host='127.0.0.1', 
            port=3306,
            database='edusense'  
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        flash(f"Error connecting to MariaDB: {e}")
        return None

@app.route('/registeruser', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        
    
        if not full_name or not email or not password:
            flash('All fields are required!')
            return redirect(url_for('register'))  
        
        
        conn = get_db_connection()
        if conn is None:
            # Connection failed, flash message handled in get_db_connection()
            return redirect(url_for('register'))  # Reload registration page
        
        cursor = conn.cursor()

        try:
            # Insert user into the database
            query = "INSERT INTO Users (full_name, email, password) VALUES (?, ?, ?)"
            cursor.execute(query, (full_name, email, password))
            conn.commit()
            flash('User successfully registered!')
        except mariadb.Error as e:
            # Log any error during insertion
            print(f"Error during user registration: {e}")
            flash(f"An error occurred while saving your information: {e}")
        finally:
            cursor.close()
            conn.close()

        # Redirect to a success page after registration
        return redirect(url_for('student_records'))  

    return render_template('RegisterUser.html')

@app.route('/success')
def success():
    return "Registration successful!"


if __name__ == '__main__':
    app.run(debug=True)

    
    """
