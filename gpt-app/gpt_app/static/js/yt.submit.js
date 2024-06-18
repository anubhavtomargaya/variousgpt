// static/js/yt.submit.js
function getYouTubeID(url) {
    var regex = /(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:watch\?v=|embed\/|v\/|.*v=)?([^&\n?#]+)|(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^&\n?#]+)/;
    var match = url.match(regex);
    return match && (match[1] || match[2]);

}

function submitYouTube() {
    var url = document.getElementById('youtubeUrl').value.trim();
    if (!url) {
        alert('Please enter a YouTube URL.');
        return;
    }

    var loader = document.getElementById('loader');
    var responseDiv = document.getElementById('response');
    loader.style.display = 'block'; // Show the loader
    responseDiv.innerHTML = ''; // Clear previous responses

    axios.post('/api/v1/gptube/yt/submit', { url: url })
    .then(function (response) {
        // Handle success response
        console.log(response.data);
        loader.style.display = 'none'; // Hide the loader
        responseDiv.innerHTML = `
            <p id="title">Title: ${response.data.title}</p>
            <p id="file_path">${response.data.file_path}</p>
            <h3 id="cost">Approx Cost:  $${response.data.whisper_approx_cost}</h3>
            <iframe width="560" height="315" src="https://www.youtube.com/embed/${getYouTubeID(url)}" frameborder="0" allowfullscreen></iframe>
            <p >Description: ${response.data.description}</p>
           
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
    })
    .catch(function (error) {
        // Handle error
        console.error('Error:', error.response.data);
        loader.style.display = 'none'; // Hide the loader
        responseDiv.innerHTML = `<p>Error: ${error.response.data.error}</p>`;
    });
}
