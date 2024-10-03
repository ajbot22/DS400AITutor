import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import subprocess

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
        # Replace this with the actual path to 'read_docs.py'
        subprocess.run(['python', 'train/read_docs.py'])
        return jsonify({"success": True, "message": "Training completed successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
