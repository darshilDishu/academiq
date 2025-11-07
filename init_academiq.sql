-- Drop and recreate the database
DROP DATABASE IF EXISTS academiq;
CREATE DATABASE academiq;
USE academiq;

-- ---------- STUDENTS ----------
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    roll_no VARCHAR(50),
    semester VARCHAR(20),
    course VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255)
);

-- ---------- ATTENDANCE ----------
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject VARCHAR(100),
    attended_lectures INT DEFAULT 0,
    total_lectures INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ---------- LIBRARY ----------
CREATE TABLE library (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    book_name VARCHAR(150),
    author VARCHAR(100),
    subject VARCHAR(100),
    status ENUM('available','borrowed') DEFAULT 'available',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ---------- COLLABORATION ----------
CREATE TABLE collaboration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ---------- TASKS ----------
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    task_name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ---------- SAMPLE DATA ----------
INSERT INTO students (name, roll_no, semester, course, email, password)
VALUES ('Aryan Kamboj', 'YMCA123', '5', 'B.Tech CSE', 'aryan@gmail.com', '1234');
