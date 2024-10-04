document.getElementById('submit-question').addEventListener('click', function() {
    const question = document.getElementById('student-question').value;

    // Send the student's question to the server
    fetch('/ask-question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {  // This will now check for the 'success' key
            updateConversation(data.response);
        } else {
            console.error("Error in response:", data.message);
        }
    })
    .catch(err => {
        console.error("Error:", err);
    });
});


// Update the conversation with new messages
function updateConversation(tutorResponse) {
    const conversationDiv = document.getElementById('conversation');
    const newMessage = document.createElement('p');
    newMessage.textContent = tutorResponse;
    conversationDiv.appendChild(newMessage);
    conversationDiv.scrollTop = conversationDiv.scrollHeight;
}
