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
    loadFiles(); // Refresh file list
  });
}

// Load user's uploaded files
async function loadFiles() {
    const res = await fetch('/my-files');
    const files = await res.json();

    const container = document.getElementById('file-list');
    container.innerHTML = ''; // clear old content

    if (files.length === 0) {
      container.innerHTML = '<p>No files uploaded yet.</p>';
      return;
    }

    const ul = document.createElement('ul');
    files.forEach(f => {
    const li = document.createElement('li');
    li.innerHTML = `
      <strong>${f.filename}</strong> 
      (Size: ${Math.round(f.file_size / 1024)} KB) – 
      Uploaded: ${f.uploaded_at} –
      <button onclick="shareFile('${f.id}')">🔗 Share</button>
      <span id="link-${f.id}"></span>
    `;
    ul.appendChild(li);
});


    container.appendChild(ul);
}

window.onload = loadFiles;

// Share file
async function shareFile(fileId) {
    console.log('Sharing file with ID:', fileId); // Debug log
    
    if (!fileId || fileId === 'undefined') {
        alert('Error: File ID is missing');
        console.error('File ID is undefined or missing');
        return;
    }
    
    try {
        const response = await fetch(`/share/${fileId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert(`File shared! Share ID: ${result.share_id}`);
            // Copy to clipboard
            copyToClipboard(`${window.location.origin}/shared/${result.share_id}`);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Share failed: ${error.message}`);
        console.error('Share error:', error);
    }
}

// Copy share link to clipboard
function copyShareLink(shareId) {
    const shareUrl = `${window.location.origin}/shared/${shareId}`;
    copyToClipboard(shareUrl);
    alert('Share link copied to clipboard!');
}

// Helper function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard:', text);
    }).catch(err => {
        console.error('Failed to copy to clipboard:', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    });
}

// Format file size for display
function formatFileSize(bytes) {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
function shareFileFromElement(element) {
    const fileId = element.closest('.file-item').dataset.fileId;
    shareFile(fileId);
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

document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  if (id) {
    document.getElementById("share-link-input").value = id;
    loadSharedFile();
  }
});


// Load on index.html
if (document.getElementById("file-list")) loadFiles();
