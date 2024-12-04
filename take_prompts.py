import os
import openai
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import DictCursor

# Load environment variables from the .env file
load_dotenv()

# Access the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database connection utility
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# Function to load context from the database
# Function to load context from the database
def load_context(student_id, course_name):
    query = """
    SELECT sc.learned_context
    FROM Student_Courses sc
    JOIN Courses c ON sc.course_id = c.id
    WHERE sc.student_id = %s AND c.name = %s
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (student_id, course_name))
            row = cursor.fetchone()
            if row:
                # Use numeric indexing to access the first column
                return row[0]
            else:
                raise ValueError("Context not found for the student and course.")

# Function to save updated context to the database
def save_context(student_id, course_id, updated_context):
    query = "UPDATE Student_Courses SET learned_context = %s WHERE student_id = %s AND course_id = %s"
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (updated_context, student_id, course_id))
            conn.commit()

# Function to generate GPT-4 response
def generate_gpt_response(student_id, course_name, user_question):
    try:
        # Fetch the student's context from the database
        context = load_context(student_id, course_name)
                
        # Call the OpenAI API using the prompt
        response = openai.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_question},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        tutor_response = response.choices[0].message.content

        # Update the context with the new interaction
        updated_context = f"{context}\n\nStudent: {user_question}\n\nTutor: {tutor_response}"

        # Fetch the course ID
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM Courses WHERE name = %s", (course_name,))
                course_row = cursor.fetchone()
                if not course_row:
                    raise ValueError("Course ID not found.")
                course_id = course_row[0]

        # Save the updated context back to the database
        save_context(student_id, course_id, updated_context)

        return tutor_response

    except Exception as e:
        return f"An error occurred: {str(e)}"
