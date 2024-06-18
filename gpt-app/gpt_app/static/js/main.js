document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('query');
    const askButton = document.getElementById('askButton');
    const responseDiv = document.getElementById('response');

    askButton.addEventListener('click', async () => {
        const query = queryInput.value.trim(); 
        console.log("query", query)
        if (!query) {
            responseDiv.textContent = 'Please enter a question.';
            return;
        }

        try {
            const response = await fetch(`/api/v1/gptube/question/Vedant_Fashions_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4`, {
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
            responseDiv.textContent = data;
        } catch (error) {
            console.error('Error querying GPT:', error);
            responseDiv.textContent = 'Error querying GPT. Please try again later.';
        }
    });
});
