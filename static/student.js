// Fetch available courses for the student
function fetchAssignedCourses() {
    fetch('/get-student-courses')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateCourseDropdown(data.courses);
            } else {
                console.error("Error fetching courses:", data.message);
            }
        })
        .catch(err => {
            console.error("Error:", err);
        });
}

// Populate the dropdown with courses
function populateCourseDropdown(courses) {
    const dropdown = document.getElementById('courses-dropdown');
    dropdown.innerHTML = ""; // Clear existing options

    courses.forEach(course => {
        const option = document.createElement('option');
        option.value = course.id; // Use course ID as the value
        option.textContent = course.name; // Display course name
        dropdown.appendChild(option);
    });
}

// Handle course switch button click
document.getElementById('switch-course-btn').addEventListener('click', () => {
    const selectedCourseId = document.getElementById('courses-dropdown').value;
    console.log("Selected course ID:", selectedCourseId);

    // This is a placeholder for future functionality
    alert(`Course switched to ID: ${selectedCourseId}`);
});

// Existing question submission functionality
document.getElementById('submit-question').addEventListener('click', function () {
    const question = document.getElementById('student-question').value;
    const coursesDropdown = document.getElementById('courses-dropdown');
    const selectedCourseName = coursesDropdown.selectedOptions[0].text;

    fetch('/ask-question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            courseName: selectedCourseName,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateConversation(data.response);
            } else {
                console.error("Error in response:", data.message);
            }
        })
        .catch(err => {
            console.error("Error:", err);
        });
});

function updateConversation(tutorResponse) {
    const conversationDiv = document.getElementById('conversation');
    const newMessage = document.createElement('p');
    newMessage.textContent = tutorResponse;
    conversationDiv.appendChild(newMessage);
    conversationDiv.scrollTop = conversationDiv.scrollHeight;
}


// Fetch courses when the page loads
document.addEventListener('DOMContentLoaded', fetchAssignedCourses);
