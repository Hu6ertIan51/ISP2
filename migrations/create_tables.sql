CREATE TABLE IF NOT EXISTS Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    mobile_number VARCHAR(15) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    school VARCHAR(255) NOT NULL,
    course VARCHAR(255) NOT NULL,
    admission_number CHAR(7) UNIQUE NOT NULL,
    current_year INT NOT NULL,
    year_intake VARCHAR(20) NOT NULL,
    international VARCHAR(50) NOT NULL,
    academic_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lecturer_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    school VARCHAR(255) NOT NULL,
    lecturer_number CHAR(7) UNIQUE NOT NULL,
    year_intake VARCHAR(20) NOT NULL,
    lecturer_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS units (
    id INT AUTO_INCREMENT PRIMARY KEY,  
    unit_name VARCHAR(255) NOT NULL,
    unit_code VARCHAR(20) NOT NULL,   
    school VARCHAR(255) NOT NULL,
    course VARCHAR(255) NOT NULL,
    year_offered INT NOT NULL,  
    semester_offered INT NOT NULL,  
    status VARCHAR(50) NOT NULL,                    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sysadmin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    staff_number VARCHAR(30) NOT NULL,
    year_registered VARCHAR(30) NOT NULL,
    admin_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS faculty_admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    school VARCHAR(255) NOT NULL,
    faculty VARCHAR(255) NOT NULL,
    faculty_number VARCHAR(30) NOT NULL,
    faculty_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);  

CREATE TABLE IF NOT EXISTS student_unit_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,  
    unit_id INT NOT NULL,
    admission_number VARCHAR(30) NOT NULL,
    unit_name VARCHAR(255) NOT NULL,    
    unit_code VARCHAR(20) NOT NULL,
    registration_status VARCHAR(50) NOT NULL, 
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_details(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lecturer_unit_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lecturer_id INT NOT NULL,
    unit_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lecturer_id) REFERENCES users(id),
    FOREIGN KEY (unit_id) REFERENCES units(id)
);

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_id INT NOT NULL,
    student_id INT NOT NULL,
    admission_number VARCHAR(255),
    class_date DATE NOT NULL,
    hours_attended INT NOT NULL,
    total_hours INT NOT NULL,
    attendance_percentage FLOAT GENERATED ALWAYS AS ((total_updated_hours / total_hours) * 100),
    absenteeism_percentage FLOAT GENERATED ALWAYS AS (100-(100 - ((hours_attended / total_hours) * 100))),
    attendance_status ENUM('Present', 'Absent') NOT NULL,
    total_updated_hours INT DEFAULT 0, -- New column for cumulative hours
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES student_details(id) ON DELETE CASCADE
);






