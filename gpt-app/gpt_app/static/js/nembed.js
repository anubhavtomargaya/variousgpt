document.addEventListener("DOMContentLoaded", function() {
    const loader = document.getElementById("loader");
    const content = document.getElementById("content");
    const tick1 = document.getElementById("tick1");
    const tick2 = document.getElementById("tick2");

    // Extract the filename from the URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const filename = urlParams.get('file');
    const extn = urlParams.get('extn');
    console.log('extn')
    console.log(extn)

    if (filename) {
        // Call the process PDF API
        if (extn === 'pdf') {


            baseUrl = '/api/v1/gptube/process/pdf';
        } else if (extn === 'json') {
            baseUrl = '/api/v1/gptube/process/tdoc';
        } else {
            // Handle other extensions or provide a default base URL if needed
            baseUrl = '/api/v1/gptube/process/pdf';
        }
        const url = 
        fetch(baseUrl, {
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
            console.log('response data',data)
            // filename = data.filename

            // Call the embed PDF API
            loader.style.display = 'block';
            console.log("using filename",data.filename)
            fetch('/api/v1/gptube/embed/doc', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ file: data.filename })
            })
            .then(response => response.json())
            .then(data => {
                // Show second tick
                loader.style.display = 'none';
                tick2.style.display = 'inline';
                window.location.href = "/view/chat/"+ data.filename;
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
