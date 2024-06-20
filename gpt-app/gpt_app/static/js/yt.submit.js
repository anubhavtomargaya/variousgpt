// static/js/yt.submit.js
function getYouTubeID(url) {
    const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[7].length == 11) ? match[7] : false;
}

function submitYouTube() {
    var url = document.getElementById('youtubeUrl').value.trim();
    if (!url) {
        alert('Please enter a YouTube URL.');
        return;
    }

    var loader = document.getElementById('loader');
    var responseDiv = document.getElementById('response');
    var videoContainer = document.getElementById('video-container');

    loader.style.display = 'block'; // Show the loader
    responseDiv.innerHTML = ''; // Clear previous responses
    videoContainer.innerHTML = ''; // Clear previous video

    axios.post('/api/v1/gptube/yt/submit', { url: url })
    .then(function (response) {
        // Handle success response
        console.log(response.data);
        loader.style.display = 'none'; // Hide the loader
        responseDiv.innerHTML = `
            <p id="title">Title: ${response.data.title}</p>
            <p id="file_path">${response.data.file_path}</p>
            <h3 id="cost">Approx Cost:  $${response.data.whisper_approx_cost}</h3>
            <p>Description: ${response.data.description}</p>
        `;

        videoContainer.innerHTML = `
            <iframe src="https://www.youtube.com/embed/${getYouTubeID(url)}" frameborder="0" allowfullscreen></iframe>
        `;
    })
    .catch(function (error) {
        // Handle error
        console.error('Error:', error.response.data);
        loader.style.display = 'none'; // Hide the loader
        responseDiv.innerHTML = `<p>Error: ${error.response.data.error}</p>`;
    });
}


function transcribeYouTube() {
    var title = document.getElementById('youtubeUrl').value.trim();
    var userPrompt = document.getElementById('contextContent').value.trim();
    if (!title) {
        alert('Please enter a YouTube URL.');
        return;
    }
    
    console.log(userPrompt)
    var loader = document.getElementById('loader');
    var responseDiv = document.getElementById('response');
    var titleElement = responseDiv.querySelector('#file_path');
    console.log(titleElement.textContent)
    loader.style.display = 'block'; // Show the loader
    responseDiv.innerHTML = ''; // Clear previous responses
    console.log("calling api")
    axios.post('/api/v1/gptube/transcribe/youtube', { title: titleElement.textContent, user_prompt: userPrompt } )
    .then(function (response) {
        
        // Handle success response
        console.log("response");
        console.log(response.data);
        loader.style.display = 'none'; // Hide the loader
        responseDiv.innerHTML = `
            <p>Transcription Result:</p>
            <pre>${response.data}</pre>
        `;
        window.location.href = "/view/embed?pl="+ titleElement.textContent.trim();
    })
    .catch(function (error) {
        // Handle error
        console.error('Error:', error.response.data);
        loader.style.display = 'none'; // Hide the loader
        responseDiv.innerHTML = `<p>Error: ${error.response.data.error}</p>`;
    });
}
