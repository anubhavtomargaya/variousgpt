document.addEventListener('DOMContentLoaded', () => {
    const questionInput = document.getElementById('question-input');
    const titleElement = document.getElementById('title');
    const answerArea = document.getElementById('answer-area');
    const loader = document.getElementById('loader');
    const leftPanel = document.getElementById('left-panel');
    const rightPanel = document.getElementById('right-panel');
    const rightButton = document.getElementById('rightButton');
    const callList = document.getElementById('call-list');
    const loader2 = document.getElementById('loader2');
    const digestResponse = document.getElementById('digestResponse');

    const queryInput = document.getElementById('question-input');
    const fileTitleElement = document.getElementById('title'); // Access the title element
    const askButton = document.getElementById('askButton');
    const responseDiv = document.getElementById('answer-area');
  
    const loader3 = document.getElementById('loader3');
    const getDigestButton = document.getElementById('getDigestButton');
    const digestResponseDiv = document.getElementById('digestResponse');
    const callListDiv = document.getElementById('callList');
    const questionListDiv = document.getElementById('answer-area');

    // askButton.addEventListener('click', async () => {
    //     const query = queryInput.value.trim();
    //     console.log("query", query);
    //     if (!query) {
    //         responseDiv.textContent = 'Please enter a question.';
    //         return;
    //     }

    //     const fileTitle = fileTitleElement.textContent; // Get the title text content
    //     console.log("fileTitle", fileTitle);

    //     // Show loader
    //     loader.style.display = 'block';
    //     responseDiv.textContent = ''; // Clear previous response

    //     try {
    //         const response = await fetch(`/api/v1/gptube/question/${fileTitle}`, {
    //             method: 'POST',
    //             headers: {
    //                 'Content-Type': 'application/json',
    //             },
    //             body: JSON.stringify({ question: query })
    //         });

    //         if (!response.ok) {
    //             throw new Error('Network response was not ok');
    //         }

    //         const data = await response.json();
    //         console.log('Response from server:', data);
    //         responseDiv.textContent = data; // Adjust based on server response structure
    //     } catch (error) {
    //         console.error('Error querying GPT:', error);
    //         responseDiv.textContent = 'Error querying GPT. Please try again later.';
    //     } finally {
    //         // Hide loader
    //         loader.style.display = 'none';
    //     }
    // });
    askButton.addEventListener('click', () => askQuestion(questionInput.value.trim()));

    // Function to fetch and display list of calls
    function fetchAndDisplayCalls() {
        loader2.style.display = 'block'; // Show loader

        fetch('/view/docs/list')
            .then(response => response.json())
            .then(data => {
                callListDiv.innerHTML = ''; // Clear previous content
                const ul = document.createElement('ul');
                // data.forEach(item => {
                //     const li = document.createElement('li');
                //     li.textContent = item; // Assuming each item is a string
                //     li.addEventListener('click', () => updateTitle(item)); // Add click event listener
                //     ul.appendChild(li);
                // });
                callListDiv.appendChild(ul);
                // console.log(Object(data))
                updateTitle(data[data.length - 1])
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
        // getDigestButton.style.display = 'block';
    }


    // Automatically fetch and display calls when window is loaded
    fetchAndDisplayCalls();
    function truncateText(text, maxLength = 15) {
        return text.length > maxLength ? text.substring(0, maxLength - 3) + "..." : text;
      }
   

    async function askQuestion(query) {
        if (!query) {
            answerArea.textContent = 'Please enter a question.';
            return;
        }

        const fileTitle = titleElement.textContent;
        loader.style.display = 'block';
        answerArea.textContent = '';

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
            answerArea.textContent = data;
            rightButton.textContent = truncateText(query)
        } catch (error) {
            console.error('Error querying GPT:', error);
            answerArea.textContent = 'Error querying GPT. Please try again later.';
        } finally {
            loader.style.display = 'none';
        }
    }

    // async function getDigest() {
    //     const fileTitle = titleElement.textContent;
    //     loader.style.display = 'block';
    //     try {
    //         const response = await fetch(`/api/v1/gptube/digest/?title=${fileTitle}`, {
    //             method: 'GET',
    //             headers: {
    //                 'Content-Type': 'application/json',
    //             }
    //         });

    //         if (!response.ok) {
    //             throw new Error('Network response was not ok');
    //         }

    //         const data = await response.json();
    //         digestResponse.textContent = data;
    //     } catch (error) {
    //         console.error('Error fetching QA Digest:', error);
    //         digestResponse.textContent = 'Error fetching digest. Please try again later.';
    //     } finally {
    //         loader.style.display = 'none';
    //     }
    // }
    async function getQuestions() {
        const fileTitle = titleElement.textContent;
        loader.style.display = 'block';
        try {
            const response = await fetch(`/view/questions/${fileTitle}`);
            const data = await response.json();
            const questionsList = document.getElementById('questionsList');
            questionsList.innerHTML = '';
            data.questions.forEach(q => {
                const li = document.createElement('li');
                li.textContent = q.question;
                li.addEventListener('click', () => {
                    questionInput.value = q.question;
                    askQuestion(q.question);
                });
                questionsList.appendChild(li);
            });
        } catch (error) {
            console.error('Error fetching questions:', error);
            document.getElementById('questionsList').innerHTML = '<li>Error fetching questions. Please try again later.</li>';
        } finally {
            loader.style.display = 'none';
        }
    }

    // Call getQuestions when the page loads
    window.addEventListener('load', getQuestions);

    // Update getQuestions call when a new file is selected
    function updateTitle(title) {
        titleElement.textContent = title;
        closePanels();
        getQuestions(); // Fetch questions for the new file
    }

    // async function getQuestions() {
    //     const fileTitle = titleElement.textContent;
    //     loader.style.display = 'block';
    //     try {
    //         const response = await fetch(`/view/questions/${fileTitle}`);
    //         const data = await response.json();
    //         const questionList = data.questions.map(q => q.question).join('\n');
    //         answerArea.textContent = `Questions for ${fileTitle}:\n${questionList}`;
    //     } catch (error) {
    //         console.error('Error fetching questions:', error);
    //         answerArea.textContent = 'Error fetching questions. Please try again later.';
    //     } finally {
    //         loader.style.display = 'none';
    //     }
    // }

    

    // questionInput.addEventListener('keypress', (e) => {
    //     if (e.key === 'Enter') {
    //         askQuestion(questionInput.value.trim());
    //     }
    // });

    // document.getElementById('askButton').addEventListener('click', () => {
    //     askQuestion(questionInput.value.trim());
    // });

});