
import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from analyzer import analyze_code
from ai_review import get_ai_review

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
@app.route("/analyze", methods=["POST"])
def upload_code():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "No file was uploaded."
        }), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:
        return jsonify({
            "success": False,
            "error": "Please select a Python file."
        }), 400

    if not uploaded_file.filename.lower().endswith(".py"):
        return jsonify({
            "success": False,
            "error": "Only Python files are supported."
        }), 400

    filename = secure_filename(uploaded_file.filename)

    try:
        code = uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        return jsonify({
            "success": False,
            "error": "The file must contain valid UTF-8 text."
        }), 400

    if not code.strip():
        return jsonify({
            "success": False,
            "error": "The Python file is empty."
        }), 400

    # Run static analysis
    try:
        findings = analyze_code(code)
    except Exception:
        app.logger.exception("Static analysis failed")
        return jsonify({
            "success": False,
            "error": "Static code analysis failed."
        }), 500

    # Run Gemini review separately
    ai_review = None
    ai_review_error = None

    try:
        ai_review = get_ai_review(code)

    except Exception as error:
        app.logger.exception("Gemini review failed")
        ai_review_error = str(error)

    return jsonify({
        "success": True,
        "filename": filename,
        "total_issues": len(findings),
        "findings": findings,
        "ai_review": ai_review,
        "ai_review_error": ai_review_error
    })


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "error": "File size must not exceed 1 MB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True, port=5000)
