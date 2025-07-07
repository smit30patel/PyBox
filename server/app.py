from flask import Flask, request, jsonify, send_file, send_from_directory, redirect
from flask_cors import CORS
import os, shutil, uuid
from metadata import SharedFile, Session, engine, Base
from r2_client import upload_to_r2, generate_download_url
from io import BytesIO

app = Flask(__name__, static_folder="../client/static", static_url_path="/")
CORS(app)

Base.metadata.create_all(engine)

# File storage setup
DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)
file_registry = {} # {file_id: {filename, owner, path, share_id}}

@app.route("/uploadfile/", methods=["POST"])
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    buffer = BytesIO(file.read())
    # Get file size
    buffer.seek(0, 2) # Move to end
    file_size = buffer.tell()
    buffer.seek(0) # Reset to start

    # Generate unique identifiers
    file_id = str(uuid.uuid4())
    share_id = file_id[:8]
    s3_key = f"uploads/{file_id}_{file.filename}"

    # Upload to Cloudflare R2
    upload_to_r2(buffer, s3_key)

    # Save metadata to DB
    session = Session()
    try:
        new_file = SharedFile(
            id=file_id,
            filename=file.filename,
            s3_key=s3_key,
            share_id=share_id,
            owner="anon",
            file_size=file_size,
            file_type=file.content_type
        )
        session.add(new_file)
        session.commit()
        print(f"File saved to database: {file.filename} with ID: {file_id}")
        
        return jsonify({
            "message": "File uploaded successfully",
            "share_id": share_id,
            "filename": file.filename
        })
    except Exception as e:
        session.rollback()
        print(f"Error saving file to database: {e}")
        return jsonify({'error': 'Failed to save file metadata'}), 500
    finally:
        session.close()

@app.route("/my-files", methods=["GET"])
def my_files():
    session = Session()
    try: 
        files = session.query(SharedFile).all()
        files_data = []
        for f in files:
            files_data.append({
                "filename": f.filename,
                "share_id": f.share_id,
                "file_size": f.file_size,
                "uploaded_at": f.created_at,
                # Add more fields if you want
            })
        return jsonify(files_data)
    except Exception as e:
        print(f"Error fetching files: {e}")
        return jsonify({'error': 'Failed to fetch files'}), 500
    finally:
        session.close()

@app.route("/share/<file_id>", methods=["POST"])
def share_file(file_id):
    session = Session()
    try:
        # Fixed: use .first() instead of .all()
        file = session.query(SharedFile).filter_by(id=file_id).first()
        if not file:
            return jsonify({"error": "File not found"}), 404

        if not file.share_id:
            file.share_id = str(uuid.uuid4())[:8]
            session.commit()
        
        return jsonify({"share_id": file.share_id})
    except Exception as e:
        session.rollback()
        print(f"Error sharing file: {e}")
        return jsonify({'error': 'Failed to share file'}), 500
    finally:
        session.close()

@app.route("/shared/<share_id>", methods=["GET"])
def get_shared_file(share_id):
    session = Session()
    try:
        # Fixed: use .first() instead of .all()
        file = session.query(SharedFile).filter_by(share_id=share_id).first()
        if not file:
            return jsonify({'error': 'File not found'}), 404

        download_url = generate_download_url(file.s3_key)
        return redirect(download_url)
    except Exception as e:
        print(f"Error getting shared file: {e}")
        return jsonify({'error': 'Failed to get shared file'}), 500
    finally:
        session.close()

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