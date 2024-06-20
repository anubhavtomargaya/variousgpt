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
});
