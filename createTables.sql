DROP TABLE Student_Courses;
DROP TABLE Courses;
DROP TABLE Students;
DROP TABLE Proctors;

-- Proctors Table
CREATE TABLE IF NOT EXISTS Proctors (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Courses Table
CREATE TABLE IF NOT EXISTS Courses (
    id SERIAL PRIMARY KEY,
    proctor_id INTEGER REFERENCES Proctors(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    context TEXT,
    filepath VARCHAR(255)
);

-- Students Table
CREATE TABLE IF NOT EXISTS Students (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Student_Courses Table (Associates Students with Courses)
CREATE TABLE IF NOT EXISTS Student_Courses (
    student_id INTEGER REFERENCES Students(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES Courses(id) ON DELETE CASCADE,
    learned_context TEXT,
    PRIMARY KEY (student_id, course_id)
);
