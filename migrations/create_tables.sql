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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

