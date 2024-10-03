const fileUploadDiv = document.getElementById('file-upload-div');
const fileInput = document.getElementById('file-input');
const previewDiv = document.getElementById('preview-div');
const trainButton = document.getElementById('train-button');

const docsFolder = "docs"; // Folder to store files

// Clicking on the div opens the file selector
fileUploadDiv.addEventListener('click', () => {
    fileInput.click();
});

// Handle file input
fileInput.addEventListener('change', handleFiles);

// Drag-and-drop functionality
fileUploadDiv.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadDiv.style.backgroundColor = '#E1261C'; // Change color when hovering with a file
});

fileUploadDiv.addEventListener('dragleave', () => {
    fileUploadDiv.style.backgroundColor = '#3DB5E6'; // Change back to original color
});

fileUploadDiv.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadDiv.style.backgroundColor = '#3DB5E6'; // Reset background
    const files = e.dataTransfer.files;
    handleFiles({ target: { files } });
});

// Function to handle files and display thumbnails
function handleFiles(event) {
    const files = event.target.files;
    for (const file of files) {
        saveFileToDocsFolder(file);
        displayFilePreview(file.name, file.type, false); // Mark file as untrained initially
    }
}

// Save file to the docs folder
function saveFileToDocsFolder(file) {
    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`${file.name} saved to docs folder.`);
        } else {
            console.error(`Error saving ${file.name}: ${data.message}`);
        }
    })
    .catch(err => console.error('Error saving file:', err));
}

// Display file preview based on file type
function displayFilePreview(fileName, fileType, isTrained) {
    const preview = document.createElement('div');
    preview.className = 'file-preview';
    if (!isTrained) {
        preview.classList.add('untrained');
    }

    const img = document.createElement('img');
    if (fileType.includes("pdf")) {
        img.src = "img/pdf.png";
    } else if (fileType.includes("pptx")) {
        img.src = "img/pptx.png";
    }

    const fileNameElement = document.createElement('div');
    fileNameElement.className = 'file-name';
    fileNameElement.textContent = fileName;

    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-icon';
    deleteButton.innerText = 'X';
    deleteButton.addEventListener('click', () => {
        preview.remove();
        removeFileFromDocsFolder(fileName);
    });

    preview.appendChild(img);
    preview.appendChild(fileNameElement);
    preview.appendChild(deleteButton);
    previewDiv.appendChild(preview);
}

// Remove file from the docs folder
function removeFileFromDocsFolder(fileName) {
    fetch(`/delete?file=${fileName}`, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`${fileName} removed from docs folder.`);
        } else {
            console.error(`Error removing ${fileName}: ${data.message}`);
        }
    })
    .catch(err => console.error('Error removing file:', err));
}

// Run the take_prompts.py script when the button is clicked
trainButton.addEventListener('click', () => {
    console.log("Running read_docs.py...");
    fetch("/train", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("Model trained successfully.");
            updateTrainedFiles();
        } else {
            console.error(`Error training model: ${data.message}`);
        }
    })
    .catch(err => console.error('Error training model:', err));
});

// Update preview after training to mark files as trained
function updateTrainedFiles() {
    const previews = document.querySelectorAll('.file-preview');
    previews.forEach(preview => {
        preview.classList.remove('untrained');
    });
}

// Function to load existing files in the docs folder
function loadExistingFiles() {
    fetch("/load-docs")
    .then(response => response.json())
    .then(files => {
        files.forEach(file => {
            displayFilePreview(file.name, file.type, file.isTrained);
        });
    })
    .catch(err => console.error("Error loading files:", err));
}

// Load existing files on page load
window.onload = loadExistingFiles;
