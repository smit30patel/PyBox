from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os, shutil, uuid

app = Flask(__name__, static_folder="../client/static", static_url_path="/")
CORS(app)

# File storage setup
DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

file_registry = {}  # {file_id: {filename, owner, path, share_id}}

@app.route("/uploadfile/", methods=["POST"])
def upload_file():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400 

    file_id = str(uuid.uuid4())
    filename = uploaded_file.filename
    file_path = os.path.join(DATASET_DIR, f"{filename}-{file_id}")

    try:
        # Read as text and save as plain text file
        with open(file_path, "w", encoding="utf-8") as dest_file:
            uploaded_text = uploaded_file.read().decode("utf-8", errors="ignore")  # decode byte to string
            dest_file.write(uploaded_text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    file_registry[file_id] = {
        "id": file_id,
        "filename": filename,
        "path": file_path,
        "owner": "user@example.com",
        "share_id": None 
    }

    return jsonify({"Success": "Uploaded File Successfully", "filename": filename})


@app.route("/my-files", methods=["GET"])
def my_files():
    return jsonify([f for f in file_registry.values() if f["owner"] == "user@example.com"])

@app.route("/share/<file_id>", methods=["POST"])
def share_file(file_id):
    if file_id not in file_registry:
        return jsonify({"error": "File not found"}), 404

    share_id = str(uuid.uuid4())[:8]
    file_registry[file_id]["share_id"] = share_id
    return jsonify({"share_id": share_id})

@app.route("/shared/<share_id>", methods=["GET"])
def get_shared_file(share_id):
    for f in file_registry.values():
        if f["share_id"] == share_id:
            return jsonify({"filename": f["filename"], "share_id": share_id})
    return jsonify({"error": "Invalid share link"}), 404

@app.route("/download/<share_id>", methods=["GET"])
def download_shared_file(share_id):
    for f in file_registry.values():
        if f["share_id"] == share_id and os.path.exists(f["path"]):
            return send_file(f["path"], as_attachment=True, download_name=f["filename"])
    return jsonify({"error": "File not found"}), 404

# Serve static frontend (HTML, CSS, JS)
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True)
