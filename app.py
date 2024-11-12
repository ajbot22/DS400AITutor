import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from google.cloud import storage
from werkzeug.utils import secure_filename
import subprocess
import json
from take_prompts import generate_gpt_response, save_context
import psycopg2
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static', template_folder='templates')

# Load environment variables
load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspace/gcloud_keys/ds400-capstone-7c0083efd90a.json"

bucket_name = "ai-tutor-docs" 
folder_prefix = "admin/"  # Folder inside the bucket for the "admin" user

# Initialize Google Cloud Storage client
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# Ensure the "admin" folder exists in the bucket
def ensure_admin_folder_exists():
    blob = bucket.blob(folder_prefix)
    if not blob.exists():
        blob.upload_from_string("", content_type="application/x-www-form-urlencoded")

ensure_admin_folder_exists()

# Check if a file has an allowed extension
ALLOWED_EXTENSIONS = {'pdf', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/proctor')
def proctor():
    return render_template('proctor.html')

# Upload file endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify(success=False, message="No file part")
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        blob = bucket.blob(f"{folder_prefix}{filename}")
        blob.upload_from_file(file)
        return jsonify(success=True, message="File uploaded")
    return jsonify(success=False, message="Invalid file")

@app.route('/load-docs', methods=['GET'])
def load_docs():
    # List files in the "admin" folder
    blobs = bucket.list_blobs(prefix=folder_prefix)
    file_list = [{'name': blob.name.replace(folder_prefix, ''), 'type': 'pdf' if blob.name.endswith('.pdf') else 'pptx'} for blob in blobs]
    return jsonify(file_list)

@app.route('/docs/<filename>')
def get_doc(filename):
    # Serve file from bucket
    blob = bucket.blob(f"{folder_prefix}{filename}")
    if blob.exists():
        file_data = blob.download_as_bytes()
        response = send_from_directory(file_data, mimetype='application/pdf' if filename.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
        return response
    return jsonify(success=False, message="File not found"), 404

# Delete file endpoint
@app.route('/delete', methods=['DELETE'])
def delete_file():
    file_name = request.args.get('file')
    blob = bucket.blob(f"{folder_prefix}{file_name}")
    if blob.exists():
        blob.delete()
        return jsonify(success=True, message="File deleted")
    return jsonify(success=False, message="File not found")

# Train model endpoint
@app.route("/train", methods=["POST"])
def train_model():
    try:
        subprocess.run(['python', 'train/read_docs.py'])
        return jsonify({"success": True, "message": "Training completed successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error occurred: {str(e)}"}), 500

# Student-specific API for asking questions
@app.route('/ask-question', methods=['POST'])
def ask_question():
    data = request.json
    user_question = data.get('question', '')
    
    # Load conversation history
    if os.path.exists("context.json"):
        with open("context.json", "r") as f:
            conversation_history = json.load(f)["context"]
    else:
        conversation_history = "You are an AI tutor but you are currently untrained."

    tutor_response, updated_history = generate_gpt_response(conversation_history, user_question)
    save_context(updated_history)
    
    return jsonify(success=True, response=tutor_response)

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")  # Either "student" or "proctor"

    table = "Students" if role == "student" else "Proctors"
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if user exists
        cursor.execute(f"SELECT id, password FROM {table} WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            # User exists, check password
            if user[1] == password:
                return jsonify({"success": True, "message": "Login successful", "route": f"/{role}"})
            else:
                return jsonify({"success": False, "message": "Incorrect password"}), 401
        else:
            # User doesn't exist, create account
            cursor.execute(f"INSERT INTO {table} (username, password) VALUES (%s, %s) RETURNING id", (username, password))
            conn.commit()
            return jsonify({"success": True, "message": "Account created", "route": f"/{role}"})
    
    finally:
        # Ensure the cursor and connection are closed
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
