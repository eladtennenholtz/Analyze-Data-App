from flask import request, jsonify
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def validate_file_upload(request):
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "Invalid file format"}), 400

    return file  

def allowed_file(filename):
    allowed_extensions = {'csv', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS