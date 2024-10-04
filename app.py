import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import subprocess
import json
from take_prompts import generate_gpt_response, save_context

app = Flask(__name__, static_folder='static', template_folder='templates')
DOCS_FOLDER = os.path.join(os.getcwd(), 'docs')
UPLOAD_FOLDER = 'docs'
ALLOWED_EXTENSIONS = {'pdf', 'pptx'}

# Ensure the docs folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify(success=True, message="File uploaded")
    return jsonify(success=False, message="Invalid file")

@app.route('/load-docs', methods=['GET'])
def load_docs():
    # Get list of all files in the docs folder
    files = os.listdir(DOCS_FOLDER)
    # Send file names along with their types (for now assume pdf or pptx)
    file_list = [{'name': f, 'type': 'pdf' if f.endswith('.pdf') else 'pptx'} for f in files]
    return jsonify(file_list)

@app.route('/docs/<path:filename>')
def get_doc(filename):
    return send_from_directory(DOCS_FOLDER, filename)

# Delete file endpoint
@app.route('/delete', methods=['DELETE'])
def delete_file():
    file_name = request.args.get('file')
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
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
        conversation_history = "You are an AI tutor but you are currently untrained, please inform the student of this and that they should wait for their proctor to train you"

    # Call GPT to generate a response (simulate the function from take_prompts.py)
    tutor_response, updated_history = generate_gpt_response(conversation_history, user_question)
    
    # Save updated context
    save_context(updated_history)
    
    # Return both the tutor's response and a success key
    return jsonify(success=True, response=tutor_response)


if __name__ == '__main__':
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
    app.run(debug=True)
