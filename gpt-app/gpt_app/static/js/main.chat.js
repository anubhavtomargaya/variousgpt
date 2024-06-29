document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('query');
    const fileTitleElement = document.getElementById('title'); // Access the title element
    const askButton = document.getElementById('askButton');
    const responseDiv = document.getElementById('response');
    const loader = document.getElementById('loader');

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
        const loader = document.getElementById('loader2');
        loader.classList.add('loader2'); // Show loader
        
        fetch('/view/docs/list')
            .then(response => response.json())
            .then(data => {
                const listDiv = document.getElementById('callList');
                listDiv.innerHTML = ''; // Clear previous content
                const ul = document.createElement('ul');
                data.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item; // Assuming each item is a string
                    li.addEventListener('click', () => updateTitle(item)); // Add click event listener
                    ul.appendChild(li);
                });
                listDiv.appendChild(ul);
            })
            .catch(error => {
                console.error('Error fetching call list:', error);
            })
            .finally(() => {
                loader.classList.remove('loader2'); // Hide loader
            });
    }

    // Function to update title
    function updateTitle(newTitle) {
        const titleElement = document.getElementById('title');
        getDigestButton.style.display = 'block';
        titleElement.textContent = newTitle;
        responseDiv.textContent = '';
    }

    // Function to fetch and display list of questions
    function fetchAndDisplayQuestions(fileTitle) {
        const loader = document.getElementById('loader3');
        loader.classList.add('loader3'); // Show loader
        
        fetch(`/view/questions/${fileTitle}`)
            .then(response => response.json())
            .then(data => {
                console.log(data,'data')
                const questionListDiv = document.getElementById('questionList');
                questionListDiv.innerHTML = ''; // Clear previous content
                const ul = document.createElement('ul');
                console.log()
                questions = data['questions']
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
                loader.classList.remove('loader3'); // Hide loader
            });
    }

    // Automatically fetch and display calls when window is loaded
    fetchAndDisplayCalls();

    // Add functionality for GET QA DIGEST
    const getDigestButton = document.getElementById('getDigestButton');
    const digestResponseDiv = document.getElementById('digestResponse');

    getDigestButton.addEventListener('click', async () => {
        const fileTitle = fileTitleElement.textContent; // Get the title text content
        console.log("fileTitle", fileTitle);

        // Show loader
        console.log(fileTitle)
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
            loader.style.display = 'none';
            getDigestButton.style.display = 'none';
            responseDiv.textContent = data;  // Display the summary from the digest
        } catch (error) {
            console.error('Error fetching QA Digest:', error);
            loader.style.display = 'none';
            responseDiv.textContent  = 'Please select a title.';
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
