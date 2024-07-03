document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('question-input');
    const fileTitleElement = document.getElementById('title'); // Access the title element
    const askButton = document.getElementById('askButton');
    const responseDiv = document.getElementById('answer-area');
    const loader = document.getElementById('loader');
    const loader2 = document.getElementById('loader2');
    const loader3 = document.getElementById('loader3');
    const getDigestButton = document.getElementById('getDigestButton');
    const digestResponseDiv = document.getElementById('digestResponse');
    const callListDiv = document.getElementById('callList');
    const questionListDiv = document.getElementById('answer-area');

    askButton.addEventListener('click', async () => {
        const query = queryInput.value.trim();
        console.log("query", query);
        if (!query) {
            responseDiv.textContent = 'Please enter a question.';
            return;
        }

        const fileTitle = fileTitleElement.textContent; // Get the title text content
        console.log("fileTitle", fileTitle);

        // Show loader
        loader.style.display = 'block';
        responseDiv.textContent = ''; // Clear previous response

        try {
            const response = await fetch(`/api/v1/gptube/question/${fileTitle}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: query })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            console.log('Response from server:', data);
            responseDiv.textContent = data; // Adjust based on server response structure
        } catch (error) {
            console.error('Error querying GPT:', error);
            responseDiv.textContent = 'Error querying GPT. Please try again later.';
        } finally {
            // Hide loader
            loader.style.display = 'none';
        }
    });

    // Function to fetch and display list of calls
    function fetchAndDisplayCalls() {
        loader2.style.display = 'block'; // Show loader

        fetch('/view/docs/list')
            .then(response => response.json())
            .then(data => {
                callListDiv.innerHTML = ''; // Clear previous content
                const ul = document.createElement('ul');
                data.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item; // Assuming each item is a string
                    li.addEventListener('click', () => updateTitle(item)); // Add click event listener
                    ul.appendChild(li);
                });
                callListDiv.appendChild(ul);
            })
            .catch(error => {
                console.error('Error fetching call list:', error);
            })
            .finally(() => {
                loader2.style.display = 'none'; // Hide loader
            });
    }

    // Function to update title
    function updateTitle(newTitle) {
        fileTitleElement.textContent = newTitle;
        responseDiv.textContent = '';
        getDigestButton.style.display = 'block';
    }

    // Function to fetch and display list of questions
    function fetchAndDisplayQuestions(fileTitle) {
        loader3.style.display = 'block'; // Show loader

        fetch(`/view/questions/${fileTitle}`)
            .then(response => response.json())
            .then(data => {
                console.log(data, 'data')
                questionListDiv.innerHTML = ''; // Clear previous content
                const ul = document.createElement('ul');
                const questions = data['questions'];
                questions.forEach(question => {
                    const li = document.createElement('li');
                    li.textContent = question['question']; // Assuming each question is a string
                    ul.appendChild(li);
                });
                questionListDiv.appendChild(ul);
            })
            .catch(error => {
                console.error('Error fetching question list:', error);
            })
            .finally(() => {
                loader3.style.display = 'none'; // Hide loader
            });
    }

    // Automatically fetch and display calls when window is loaded
    fetchAndDisplayCalls();

    // Add functionality for GET QA DIGEST
    getDigestButton.addEventListener('click', async () => {
        const fileTitle = fileTitleElement.textContent; // Get the title text content
        console.log("fileTitle", fileTitle);

        // Show loader
        loader.style.display = 'block';
        try {
            const response = await fetch(`/api/v1/gptube/digest/?title=${fileTitle}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            console.log('Response from server:', data);
            digestResponseDiv.textContent = data; // Display the summary from the digest
        } catch (error) {
            console.error('Error fetching QA Digest:', error);
            digestResponseDiv.textContent = 'Error fetching digest. Please try again later.';
        } finally {
            loader.style.display = 'none'; // Hide loader
        }
    });

    // Add event listener for the GET QUESTIONS button
    const getQuestionsButton = document.getElementById('getQuestionsButton');
    getQuestionsButton.addEventListener('click', () => {
        const fileTitle = fileTitleElement.textContent; // Get the title text content
        if (fileTitle) {
            fetchAndDisplayQuestions(fileTitle);
        } else {
            console.error('No title selected');
        }
    });
    
});
