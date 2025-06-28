// Upload file
const uploadForm = document.getElementById("upload-form");
if (uploadForm) {
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("file-input");
    const formData = new FormData();
    formData.append("file", input.files[0]);

    const res = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();

    document.getElementById("upload-status").textContent = res.ok ? "✅ Uploaded" : "❌ Upload failed";
    loadMyFiles(); // Refresh file list
  });
}

// Load user's uploaded files
async function loadMyFiles() {
  const res = await fetch("/api/my-files");
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
  const res = await fetch(`/api/share/${fileId}`, { method: "POST" });
  const data = await res.json();
  document.getElementById(`link-${fileId}`).innerText = `Link: /share.html?id=${data.share_id}`;
}

// Recipient views file
async function loadSharedFile() {
  const shareId = document.getElementById("share-link-input").value;
  if (!shareId) return;

  const res = await fetch(`/api/shared/${shareId}`);
  const infoDiv = document.getElementById("shared-file-info");

  if (!res.ok) {
    infoDiv.textContent = "❌ Invalid or expired share link";
    return;
  }

  const data = await res.json();
  infoDiv.innerHTML = `
    <p>Shared File: ${data.filename}</p>
    <a href="/api/download/${shareId}" download>Download</a>
  `;
}

// Load on index.html
if (document.getElementById("file-list")) loadMyFiles();
