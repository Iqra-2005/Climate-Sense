// Main JavaScript for index page

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('usernameForm');
    const errorMessage = document.getElementById('errorMessage');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        
        if (!username) {
            showError('Please enter your name');
            return;
        }

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: username })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Redirect to dashboard
                window.location.href = '/dashboard';
            } else {
                showError(data.error || 'Failed to register. Please try again.');
            }
        } catch (error) {
            showError('Network error. Please try again.');
            console.error('Error:', error);
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
});
