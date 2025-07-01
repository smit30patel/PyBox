from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os, shutil, uuid
# from pydentic import BaseModel

app = FastAPI()

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../client/static"))

# Mount client static files to serve HTML/JS/CSS from root
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="client")

# File storage
DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)
file_registry = {}  # {file_id: {filename, owner, path, share_id}}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    # file_id = str(uuid.uuid4())
    # file_path = os.path.join(DATASET_DIR, f"{file.filename}-{file_id}")
    # with open(file_path, "wb") as f:
    #     shutil.copyfileobj(file.file, f)
    # file_registry[file_id] = { 
    #     "id": file_id, 
    #     "filename": file.filename,
    #     "path": file_path, 
    #     "owner": "user@example.com",    
    #     "share_id": None
    # }
    # return JSONResponse(status_code=200, content={"Success": "Uploaded File Successfully", "filename": file.filename})
    print("Working......")  

@app.get("/my-files")
def my_files():
    # return [f for f in file_registry.values() if f["owner"] == "user@example.com"]
    return file_registry.values()
@app.post("/share/{file_id}")
def share_file(file_id: str):
    if file_id not in file_registry:
        return JSONResponse(status_code=404, content={"error": "File not found"})
    
    share_id = str(uuid.uuid4())[:8]
    file_registry[file_id]["share_id"] = share_id
    return {"share_id": share_id}

@app.get("/shared/{share_id}")
def get_shared_file(share_id: str):
    for f in file_registry.values():
        if f["share_id"] == share_id:
            return {"filename": f["filename"], "share_id": share_id}
    return JSONResponse(status_code=404, content={"error": "Invalid share link"})

@app.get("/download/{share_id}")
def download_shared_file(share_id: str):
    for f in file_registry.values():
        if f["share_id"] == share_id and os.path.exists(f["path"]):
            return FileResponse(f["path"], filename=f["filename"])
    return JSONResponse(status_code=404, content={"error": "File not found"})
