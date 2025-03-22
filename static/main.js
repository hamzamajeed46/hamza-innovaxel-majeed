document.addEventListener('DOMContentLoaded', () => {
    // Update URL functionality
    const updateForm = document.getElementById('update-form');
    const updateResult = document.getElementById('update-result');

    updateForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const shortCode = document.getElementById('short_code_update').value;
        const newOriginalUrl = document.getElementById('new_original_url').value;

        if (!shortCode || !newOriginalUrl) {
            updateResult.innerHTML = '<p style="color: red;">Both fields are required.</p>';
            return;
        }

        try {
            const response = await fetch(`/shorten/${shortCode}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ original_url: newOriginalUrl }),
            });

            const data = await response.json();

            if (response.ok) {
                updateResult.innerHTML = `<p style="color: green;">${data.message}</p>`;
            } else {
                updateResult.innerHTML = `<p style="color: red;">${data.error}</p>`;
            }
        } catch (error) {
            updateResult.innerHTML = '<p style="color: red;">An error occurred while updating the URL.</p>';
        }
    });

    // Delete URL functionality
    const deleteForm = document.getElementById('delete-form');
    const deleteResult = document.getElementById('delete-result');

    deleteForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const shortCode = document.getElementById('short_code_delete').value;

        if (!shortCode) {
            deleteResult.innerHTML = '<p style="color: red;">Short code is required.</p>';
            return;
        }

        try {
            const response = await fetch(`/shorten/${shortCode}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();

            if (response.ok) {
                deleteResult.innerHTML = `<p style="color: green;">${data.message}</p>`;
            } else {
                deleteResult.innerHTML = `<p style="color: red;">${data.error}</p>`;
            }
        } catch (error) {
            deleteResult.innerHTML = '<p style="color: red;">An error occurred while deleting the URL.</p>';
        }
    });

    // Statistics functionality
    const statsForm = document.getElementById('stats-form');
    const statsResult = document.getElementById('stats-result');

    statsForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const shortCode = document.getElementById('short_code_stats').value;

        if (!shortCode) {
            statsResult.innerHTML = '<p class="error">Short code is required.</p>';
            return;
        }

        try {
            const response = await fetch(`/shorten/${shortCode}/stats`);
            const data = await response.json();

            if (response.ok) {
                const dateOptions = {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    timeZoneName: 'short'
                };

                const formatDate = (dateStr) => {
                    try {
                        return new Date(dateStr).toLocaleString('en-US', dateOptions);
                    } catch (err) {
                        return 'Date not available';
                    }
                };

                statsResult.innerHTML = `
                    <div class="stats-item">
                        <strong>Original URL:</strong>
                        <a href="${data.original_url}" target="_blank">${data.original_url}</a>
                    </div>
                    <div class="stats-item">
                        <strong>Short Code:</strong>
                        <span>${data.short_code}</span>
                    </div>
                    <div class="stats-item">
                        <strong>Created:</strong>
                        <span>${formatDate(data.created_at)}</span>
                    </div>
                    <div class="stats-item">
                        <strong>Last Updated:</strong>
                        <span>${formatDate(data.updated_at)}</span>
                    </div>
                    <div class="stats-item">
                        <strong>Total Clicks:</strong>
                        <span>${data.access_count}</span>
                    </div>
                `;
            } else {
                statsResult.innerHTML = `<p class="error">${data.error}</p>`;
            }
        } catch (error) {
            console.error('Error:', error);
            statsResult.innerHTML = '<p class="error">An error occurred while fetching statistics.</p>';
        }
    });
});