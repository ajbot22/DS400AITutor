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
    console.log(event)
    const coursesDropdown = document.getElementById('courses-dropdown');
    const files = event.target.files;
    const selectedCourse = coursesDropdown.value;
    const selectedCourseName = coursesDropdown.selectedOptions[0].text;  // This gets the course name
    // if the above name call doesnt work, consider .text instead (data seemed to contain the text but maybe it doesnt always?)
    if (!selectedCourseName) {
        alert("Please select a course before uploading files.");
        return;
    }

    for (const file of files) {
        saveFileToDocsFolder(file, selectedCourseName); // Pass selected course
        displayFilePreview(file.name, file.type, false); // Mark file as untrained initially
    }
}

// Save file to the appropriate course's folder
function saveFileToDocsFolder(file, course) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("course", course); // course name

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`${file.name} saved to ${course} folder.`);
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

function removeFileFromDocsFolder(fileName) {
    const coursesDropdown = document.getElementById('courses-dropdown');
    const selectedCourse = coursesDropdown.value;
    const selectedCourseName = coursesDropdown.selectedOptions[0].text;  // This gets the course name

    if (!selectedCourseName) {
        alert("Please select a course.");
        return;
    }
    console.log(fileName)
    console.log(selectedCourseName)
    fetch(`/delete?file=${fileName}&course=${selectedCourseName}`, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`${fileName} removed from ${selectedCourseName} folder.`);
        } else {
            console.error(`Error removing ${fileName}: ${data.message}`);
        }
    })
    .catch(err => console.error('Error removing file:', err));
}

// Run the take_prompts.py script when the button is clicked
trainButton.addEventListener('click', () => {
    console.log("Running read_docs.py...");
    const coursesDropdown = document.getElementById('courses-dropdown');
    const selectedCourseName = coursesDropdown.selectedOptions[0].text;  // This gets the course name
    console.log("Trying to train for course"+selectedCourseName)
    if (!selectedCourseName) {
        alert("Please select a course.");
        return;
    }

    fetch("/train", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ course_name: selectedCourseName })
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

document.getElementById('assign-student-btn').addEventListener('click', () => {
    const studentUsername = document.getElementById('student-username').value.trim();
    const coursesDropdown = document.getElementById('courses-dropdown'); 
    const selectedCourseName = coursesDropdown.selectedOptions[0].text;  // This gets the course name.

    if (!studentUsername) {
        alert("Please enter a student username.");
        return;
    }

    fetch('/assign-student', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: studentUsername, 
            course_name: selectedCourseName 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Student "${studentUsername}" successfully assigned to the course "${selectedCourseName}".`);
        } else {
            alert(`Error: ${data.message}`);
        }
    })
    .catch(err => {
        console.error('Error assigning student:', err);
        alert('An error occurred while assigning the student.');
    });
});

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

document.addEventListener('DOMContentLoaded', function () {
    const coursesDropdown = document.getElementById('courses-dropdown');
    const addCourseBtn = document.getElementById('add-course-btn');
    const modal = document.getElementById('add-course-modal');
    const saveCourseBtn = document.getElementById('save-course-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const courseNameInput = document.getElementById('course-name-input');

    // Open the modal
    addCourseBtn.addEventListener('click', function () {
        modal.style.display = 'flex';
    });

    // Close the modal
    closeModalBtn.addEventListener('click', function () {
        modal.style.display = 'none';
    });

    // Fetch courses from the server
    fetch('/get-courses')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Populate the dropdown menu
                data.courses.forEach(course => {
                    const option = document.createElement('option');
                    option.value = course.id;
                    option.textContent = course.name;
                    coursesDropdown.appendChild(option);
                });
            } else {
                console.error(data.message);
            }
        })
        .catch(error => console.error('Error fetching courses:', error));

    // Save the new course
    saveCourseBtn.addEventListener('click', function () {
        const courseName = courseNameInput.value.trim();

        if (!courseName) {
            alert('Please enter a course name.');
            return;
        }

        fetch('/add-course', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: courseName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Course added successfully!');
                // Add the new course to the dropdown
                const option = document.createElement('option');
                option.value = data.course_id;
                option.textContent = courseName;
                coursesDropdown.appendChild(option);

                // Close the modal and clear the input
                modal.style.display = 'none';
                courseNameInput.value = '';
            } else {
                alert('Error adding course: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error adding course:', error);
            alert('An unexpected error occurred.');
        });
    });
});


// Load existing files on page load
window.onload = loadExistingFiles;
