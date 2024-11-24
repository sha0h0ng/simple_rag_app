from flask import Flask, request, jsonify, send_file
from services.index_service import IndexService
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import logging


app = Flask(__name__)

# Enable CORS for all routes
# Please note that this is for development purposes only.
# In a production environment, you should restrict CORS to specific origins.
CORS(app)


app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

index_service = IndexService()


@app.route('/')
def index():
    return send_file('templates/index.html')


@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'files[]' not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            return jsonify({"error": "No files selected"}), 400

        saved_paths = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                saved_paths.append(filepath)
                logger.debug(f"Saved file: {filepath}")

        if not saved_paths:
            return jsonify({"error": "No files were successfully saved"}), 400

        try:
            result = index_service.create_index(app.config['UPLOAD_FOLDER'])
            logger.debug(f"Index created with result: {result}")
            return jsonify(result)
        finally:
            # Clean up uploaded files
            for filepath in saved_paths:
                try:
                    os.remove(filepath)
                    logger.debug(f"Cleaned up file: {filepath}")
                except Exception as e:
                    logger.error(f"Error cleaning up file {
                                 filepath}: {str(e)}")

    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/query", methods=["POST"])
def query():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        if "question" not in data:
            return jsonify({"error": "Missing question parameter"}), 400

        template_type = data.get("template_type", "default")
        logger.debug(f"Using template: {template_type}")

        response = index_service.query(
            question=data["question"],
            similarity_top_k=data.get("top_k", 3),
            template_type=template_type
        )
        return jsonify(response)

    except ValueError as ve:
        logger.warning(f"Value error in query: {str(ve)}")
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        logger.error(f"Query error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/query', methods=['OPTIONS'])
def query_preflight():
    return '', 204


@app.route("/templates", methods=["GET"])
def get_templates():
    """Return available template types"""
    return jsonify(list(index_service.qa_templates.keys()))


if __name__ == "__main__":
    app.run(debug=True, port=5050, host="0.0.0.0")
