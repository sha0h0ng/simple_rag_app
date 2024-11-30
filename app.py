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
        logger.debug("Starting file upload process")
        if 'files[]' not in request.files:
            logger.warning("No files found in request")
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            logger.warning("Empty file list or filename received")
            return jsonify({"error": "No files selected"}), 400

        saved_paths = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                logger.info(f"Attempting to save file: {filename}")
                file.save(filepath)
                saved_paths.append(filepath)
                logger.debug(f"Successfully saved file: {filepath}")

        if not saved_paths:
            logger.warning("No files were successfully saved")
            return jsonify({"error": "No files were successfully saved"}), 400

        try:
            logger.info("Creating index from uploaded files")
            result = index_service.create_index(app.config['UPLOAD_FOLDER'])
            logger.debug(f"Index created successfully with result: {result}")
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}", exc_info=True)
            raise
        finally:
            # Clean up uploaded files
            logger.info("Starting cleanup of uploaded files")
            for filepath in saved_paths:
                try:
                    os.remove(filepath)
                    logger.debug(f"Successfully cleaned up file: {filepath}")
                except Exception as e:
                    logger.error(f"Error cleaning up file {
                                 filepath}: {str(e)}", exc_info=True)

    except Exception as e:
        logger.error(f"Upload process failed: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/query", methods=["POST"])
def query():
    try:
        logger.debug("Starting query process")
        data = request.json
        if not data:
            logger.warning("No data provided in request")
            return jsonify({"error": "No data provided"}), 400

        if "question" not in data:
            logger.warning("Missing question parameter in request")
            return jsonify({"error": "Missing question parameter"}), 400

        template_type = data.get("template_type", "default")
        logger.info(f"Processing query with template type: {template_type}")
        logger.debug(f"Query parameters: question='{
                     data['question']}', top_k={data.get('top_k', 3)}")

        response = index_service.query(
            question=data["question"],
            similarity_top_k=data.get("top_k", 3),
            template_type=template_type
        )
        logger.debug(f"Query completed successfully with response: {response}")
        return jsonify(response)

    except ValueError as ve:
        logger.warning(f"Invalid query parameters: {str(ve)}", exc_info=True)
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        logger.error(f"Query process failed: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/query-account", methods=["POST"])
def query_account():
    try:
        logger.debug("Starting query process")
        data = request.json
        if not data:
            logger.warning("No data provided in request")
            return jsonify({"error": "No data provided"}), 400

        if "transaction_data" not in data:
            logger.warning("Missing transaction_data parameter in request")
            return jsonify({"error": "Missing transaction_data parameter"}), 400

        response = index_service.query_account(
            transaction_data=data["transaction_data"]
        )
        logger.debug(f"Query completed successfully with response: {response}")

        return jsonify(response)

    except ValueError as ve:
        logger.warning(f"Invalid query parameters: {str(ve)}", exc_info=True)
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        logger.error(f"Query process failed: {str(e)}", exc_info=True)
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
