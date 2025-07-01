// Upload file
const uploadForm = document.getElementById("upload-form");
const BASE_URL = "http://localhost:8000";
const status_back = document.getElementById("message");
if (uploadForm) {
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("file-input");
    if (input.files.length === 0) {
        status_back.textContent = "Please select a file to upload.";
        return;
      }
    const formData = new FormData();
    formData.append("file", input.files[0]);

    const res = await fetch('/uploadfile/', { method: "POST", body: formData });
    const data = await res.json();

    status_back.textContent = res.ok ? "✅ Uploaded" : "❌ Upload failed";
    loadMyFiles(); // Refresh file list
  });
}

// Load user's uploaded files
async function loadMyFiles() {
  const res = await fetch("/my-files");
  const files = await res.json();
  const list = document.getElementById("file-list");
  list.innerHTML = "";
  files.forEach(file => {
    const li = document.createElement("li");
    li.innerHTML = `
      ${file.filename} 
      <button onclick="shareFile('${file.id}')">Generate Share Link</button>
      <span id="link-${file.id}"></span>
    `;
    list.appendChild(li);
  });
}

// Share file
async function shareFile(fileId) {
  const res = await fetch(`/share/${fileId}`, { method: "POST" });
  const data = await res.json();
  document.getElementById(`link-${fileId}`).innerText = `Link: /share.html?id=${data.share_id}`;
}

// Recipient views file
async function loadSharedFile() {
  const shareId = document.getElementById("share-link-input").value;
  if (!shareId) return;

  const res = await fetch(`/shared/${shareId}`);
  const infoDiv = document.getElementById("shared-file-info");

  if (!res.ok) {
    infoDiv.textContent = "❌ Invalid or expired share link";
    return;
  }

  const data = await res.json();
  infoDiv.innerHTML = `
    <p>Shared File: ${data.filename}</p>
    <a href="/download/${shareId}" download>Download</a>
  `;
}

// Load on index.html
if (document.getElementById("file-list")) loadMyFiles();
