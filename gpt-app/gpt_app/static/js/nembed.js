document.addEventListener("DOMContentLoaded", function() {
    const loader = document.getElementById("loader");
    const content = document.getElementById("content");
    const tick1 = document.getElementById("tick1");
    const tick2 = document.getElementById("tick2");

    // Extract the filename from the URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const filename = urlParams.get('file');

    if (filename) {
        // Call the process PDF API
        fetch('/api/v1/gptube/process/pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file: filename })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loader and show first tick
            loader.style.display = 'none';
            content.style.display = 'block';
            tick1.style.display = 'inline';

            // Call the embed PDF API
            fetch('/api/v1/gptube/embed/pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ file: filename })
            })
            .then(response => response.json())
            .then(data => {
                // Show second tick
                tick2.style.display = 'inline';
            })
            .catch(error => {
                console.error('Error embedding PDF:', error);
            });
        })
        .catch(error => {
            console.error('Error processing PDF:', error);
        });
    } else {
        console.error('Filename not provided');
    }
});
