window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');
    const error = params.get('error');
    const errorDescription = params.get('error_description'); // Some providers might send this

    const messageArea = document.getElementById('callbackMessageArea');

    const saveTokensInCallback = (accToken, refToken) => {
        localStorage.setItem('accessToken', accToken);
        localStorage.setItem('refreshToken', refToken);
    };

    const clearTokensInCallback = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    };

    if (accessToken && refreshToken) {
        if (messageArea) messageArea.textContent = 'Login successful! Redirecting...'; // User feedback
        saveTokensInCallback(accessToken, refreshToken);
        // Redirect to the main page, which will then handle UI updates
        window.location.href = 'index.html';
    } else if (error) {
        let errorMessage = `OAuth Error: ${error}`;
        if (errorDescription) {
            errorMessage += ` - ${errorDescription}`;
        }
        if (messageArea) {
            messageArea.textContent = errorMessage + ' Redirecting...';
            messageArea.style.color = 'red';
        } else {
            // Fallback if messageArea is not found for some reason
            console.error(errorMessage);
        }
        clearTokensInCallback(); // Clear any partial tokens just in case
        // Redirect to main page, which can then show a generic login error or state
        // Optionally, append error to URL: window.location.href = `index.html#error=${encodeURIComponent(error)}`;
        setTimeout(() => { // Give a moment for the user to see the message
            window.location.href = 'index.html';
        }, 2000); // 2-second delay
    } else {
        // No tokens and no error, or unexpected state.
        // This could happen if the user navigates to oauth_callback.html directly.
        if (messageArea) messageArea.textContent = 'No login information found. Redirecting...';
        // Redirect to main page.
        setTimeout(() => { // Give a moment for the user to see the message
             window.location.href = 'index.html';
        }, 1000); // 1-second delay
    }
});
