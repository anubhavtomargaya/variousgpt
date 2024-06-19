document.addEventListener('DOMContentLoaded', () => {
    const viewButton = document.getElementById('viewButton');
    const fetchDataButton = document.getElementById('fetchDataButton');
    const transcriptDiv = document.getElementById('transcript');
    const apiDataDiv = document.getElementById('apiData');
    const loaderDiv = document.getElementById('loader');

    viewButton.addEventListener('click', async () => {
        const fileNameInput = document.getElementById('fileName');
        const fileName = fileNameInput.value.trim();

        if (!fileName) {
            transcriptDiv.textContent = 'Please enter a file name.';
            return;
        }

        try {
            loaderDiv.style.display = 'block';
            transcriptDiv.textContent = '';

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
    });

    fetchDataButton.addEventListener('click', async () => {
        try {
            const response = await axios.get(`/view/transcript/${fileName}`);

            if (response.status !== 200) {
                throw new Error('Network response was not ok');
            }

            apiDataDiv.textContent = JSON.stringify(response.data, null, 2);
        } catch (error) {
            console.error('Error fetching data:', error);
            apiDataDiv.textContent = 'Error fetching data. Please try again later.';
        }
    });
});
