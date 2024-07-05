document.addEventListener('DOMContentLoaded', async () => {
    const viewButton = document.getElementById('viewButton');
    const fetchDataButton = document.getElementById('fetchDataButton');
    const transcriptDiv = document.getElementById('transcript');
    const apiDataDiv = document.getElementById('apiData');
    const loaderDiv = document.getElementById('loader');
    const fileNameInput = document.getElementById('fileName');
    
    const fetchTranscript = async (fileName) => {
        try {
            loaderDiv.style.display = 'block';
            transcriptDiv.textContent = '';

            // const response = await axios.get(`/view/transcript/${fileName}`);
            const response = await axios.get(`/view/transcript/${fileName}`);

            if (response.status !== 200) {
                throw new Error('Network response was not ok');
            }

            transcriptDiv.textContent = response.data;
        } catch (error) {
            console.error('Error fetching transcript:', error);
            transcriptDiv.textContent = 'Error fetching transcript. Please try again later.';
        } finally {
            loaderDiv.style.display = 'none';
        }
    };

    viewButton.addEventListener('click', () => {
        const fileName = fileNameInput.value.trim();
        if (!fileName) {
            transcriptDiv.textContent = 'Please enter a file name.';
            return;
        }
        fetchTranscript(fileName);
    });

    // Automatically fetch transcript on page load
    const initialFileName = fileNameInput.value.trim();
    if (initialFileName) {
        fetchTranscript(initialFileName);
    }

    
});
