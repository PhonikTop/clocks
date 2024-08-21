document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('shorten-form');
    const urlInput = document.getElementById('url-input');
    const linksList = document.getElementById('links-list');

    // Function to add a link to the list
    function addLinkToList(shortUrl, originalUrl) {
        const listItem = document.createElement('li');
        listItem.innerHTML = `<a href="${shortUrl}" target="_blank">${shortUrl}</a> - ${originalUrl}`;
        linksList.appendChild(listItem);
    }

    // Function to fetch existing links
    function fetchLinks() {
        fetch('/api/links/')
            .then(response => response.json())
            .then(data => {
                linksList.innerHTML = '';
                data.links.forEach(link => {
                    addLinkToList(link.short_url, link.original_url);
                });
            });
    }

    // Handle form submission
    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const url = urlInput.value;
        fetch('/api/shorten/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ url })
        })
        .then(response => response.json())
        .then(data => {
            addLinkToList(data.short_url, data.original_url);
            urlInput.value = '';
        });
    });

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Fetch and display links on page load
    fetchLinks();
});
