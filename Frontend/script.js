// Base URL of your backend API
const BASE_URL = 'http://localhost:8000';

// Handle User Input Form Submission
document.getElementById('user-input-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const areaOfInterest = document.getElementById('area-of-interest').value;
    const contentType = document.getElementById('content-type').value;
    const keywords = document.getElementById('keywords').value.split(',').map(k => k.trim());
    const postFrequency = parseInt(document.getElementById('post-frequency').value);

    const payload = {
        area_of_interest: areaOfInterest,
        content_type: contentType,
        keywords: keywords,
        post_frequency: postFrequency
    };

    try {
        const response = await fetch(`${BASE_URL}/user-input`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert('User input submitted successfully.');
            // Wait for the backend to process
            setTimeout(fetchGeneratedContent, 5000);
        } else {
            const errorData = await response.json();
            alert('Error submitting user input: ' + errorData.detail);
        }
    } catch (error) {
        alert('Error submitting user input: ' + error.message);
    }
});

// Fetch Generated Content
async function fetchGeneratedContent() {
    try {
        const response = await fetch(`${BASE_URL}/state`);
        if (response.ok) {
            const state = await response.json();
            if (state.generated_content && state.generated_content.length > 0) {
                displayGeneratedContent(state.generated_content[0]);
                document.getElementById('generated-content-section').style.display = 'block';
            } else {
                // Wait and retry if content not yet generated
                setTimeout(fetchGeneratedContent, 3000);
            }
        } else {
            const errorData = await response.json();
            alert('Error fetching state: ' + errorData.detail);
        }
    } catch (error) {
        alert('Error fetching state: ' + error.message);
    }
}

// Display Generated Content
function displayGeneratedContent(content) {
    const contentDiv = document.getElementById('generated-content');
    contentDiv.innerHTML = `
        <p><strong>Day:</strong> ${content.day}</p>
        <p><strong>Topic:</strong> ${content.topic}</p>
        <p><strong>Content:</strong></p>
        <p>${content.content}</p>
    `;
}

// Handle Feedback Form Submission
document.getElementById('feedback-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const liked = document.getElementById('liked').value === 'true';
    const comments = document.getElementById('comments').value;

    const payload = {
        liked: liked,
        comments: comments
    };

    try {
        const response = await fetch(`${BASE_URL}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert('Feedback submitted successfully.');
            // Wait for the backend to process
            setTimeout(fetchAllGeneratedContent, 10000);
        } else {
            const errorData = await response.json();
            alert('Error submitting feedback: ' + errorData.detail);
        }
    } catch (error) {
        alert('Error submitting feedback: ' + error.message);
    }
});

// Fetch All Generated Content
async function fetchAllGeneratedContent() {
    try {
        const response = await fetch(`${BASE_URL}/state`);
        if (response.ok) {
            const state = await response.json();
            if (state.generated_content && state.generated_content.length > 0) {
                displayAllGeneratedContent(state.generated_content);
                document.getElementById('all-content-section').style.display = 'block';
            } else {
                // Wait and retry if content not yet generated
                setTimeout(fetchAllGeneratedContent, 3000);
            }
        } else {
            const errorData = await response.json();
            alert('Error fetching state: ' + errorData.detail);
        }
    } catch (error) {
        alert('Error fetching state: ' + error.message);
    }
}

// Display All Generated Content
function displayAllGeneratedContent(contents) {
    const contentDiv = document.getElementById('all-generated-content');
    contentDiv.innerHTML = '';
    contents.forEach(content => {
        contentDiv.innerHTML += `
            <div class="content-item">
                <p><strong>Day:</strong> ${content.day}</p>
                <p><strong>Topic:</strong> ${content.topic}</p>
                <p><strong>Content:</strong></p>
                <p>${content.content}</p>
                <hr>
            </div>
        `;
    });
}
