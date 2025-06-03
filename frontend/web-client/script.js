document.addEventListener('DOMContentLoaded', () => {
    const BASE_URL = 'http://127.0.0.1:5000'; // Adjust if your backend runs elsewhere

    // Get DOM elements
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const signupButton = document.getElementById('signupButton');
    const loginButton = document.getElementById('loginButton');
    const logoutButton = document.getElementById('logoutButton');
    const refreshTokenButton = document.getElementById('refreshTokenButton');
    const fetchProtectedButton = document.getElementById('fetchProtectedButton');
    const protectedDataOutput = document.getElementById('protectedDataOutput');
    const messageArea = document.getElementById('messageArea');

    // --- Token Storage ---
    const saveTokens = (accessToken, refreshToken) => {
        localStorage.setItem('accessToken', accessToken);
        if (refreshToken) { // Refresh token might not always be updated/present
            localStorage.setItem('refreshToken', refreshToken);
        }
    };

    const getTokens = () => {
        return {
            accessToken: localStorage.getItem('accessToken'),
            refreshToken: localStorage.getItem('refreshToken')
        };
    };

    const clearTokens = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    };

    // --- Display Messages ---
    const displayMessage = (message, isError = false) => {
        messageArea.textContent = message;
        if (isError) {
            messageArea.className = 'error';
        } else {
            messageArea.className = 'success';
        }
    };

    const clearMessage = () => {
        messageArea.textContent = '';
        messageArea.className = '';
    };

    // --- API Call Helper ---
    async function apiCall(endpoint, method = 'GET', body = null, requiresAuth = false) {
        const headers = {
            'Content-Type': 'application/json'
        };
        const tokens = getTokens();

        if (requiresAuth) {
            if (!tokens.accessToken) {
                displayMessage('Access token not found. Please login.', true);
                return null; // Or throw error
            }
            headers['Authorization'] = `Bearer ${tokens.accessToken}`;
        }

        // Special case for refresh token, it uses the refresh token in Bearer
        if (endpoint === '/refresh') {
             if (!tokens.refreshToken) {
                displayMessage('Refresh token not found. Please login.', true);
                return null;
            }
            headers['Authorization'] = `Bearer ${tokens.refreshToken}`;
        }


        try {
            const config = {
                method: method,
                headers: headers
            };
            if (body) {
                config.body = JSON.stringify(body);
            }

            const response = await fetch(BASE_URL + endpoint, config);
            const data = await response.json(); // Try to parse JSON regardless of status for error messages

            if (!response.ok) {
                displayMessage(data.msg || `Error: ${response.status} ${response.statusText}`, true);
                if (response.status === 401 && endpoint === '/refresh') { // Unauthorized on refresh
                    clearTokens(); // Clear tokens if refresh fails due to auth
                }
                return null;
            }
            return data;
        } catch (error) {
            console.error('API Call Error:', error);
            displayMessage('Network error or server is not responding.', true);
            return null;
        }
    }

    // --- Event Listeners ---

    signupButton.addEventListener('click', async () => {
        clearMessage();
        const email = emailInput.value;
        const password = passwordInput.value;
        if (!email || !password) {
            displayMessage('Email and password are required for signup.', true);
            return;
        }
        const data = await apiCall('/signup', 'POST', { email, password });
        if (data) {
            displayMessage(data.msg || 'Signup successful!');
        }
    });

    loginButton.addEventListener('click', async () => {
        clearMessage();
        const email = emailInput.value;
        const password = passwordInput.value;
        if (!email || !password) {
            displayMessage('Email and password are required for login.', true);
            return;
        }
        const data = await apiCall('/login', 'POST', { email, password });
        if (data && data.access_token) {
            saveTokens(data.access_token, data.refresh_token);
            displayMessage('Login successful!');
            emailInput.value = ''; // Clear fields after successful login
            passwordInput.value = '';
        }
    });

    logoutButton.addEventListener('click', async () => {
        clearMessage();
        const tokens = getTokens();
        if (!tokens.accessToken) {
            displayMessage('You are not logged in.', true);
            return;
        }
        // For logout, the requiresAuth flag will add the access token to header
        const data = await apiCall('/logout', 'POST', null, true);
        if (data) {
            displayMessage(data.msg || 'Logout successful!');
        }
        clearTokens(); // Always clear tokens on logout attempt
        protectedDataOutput.textContent = 'Protected data will appear here...'; // Clear protected data
    });

    refreshTokenButton.addEventListener('click', async () => {
        clearMessage();
        const tokens = getTokens();
        if (!tokens.refreshToken) {
            displayMessage('No refresh token available. Please login again.', true);
            return;
        }
        // apiCall handles adding refresh token to header for '/refresh' endpoint
        const data = await apiCall('/refresh', 'POST', null, false); // Auth handled by specific logic in apiCall for /refresh
        if (data && data.access_token) {
            saveTokens(data.access_token, tokens.refreshToken); // Save new access token, keep old refresh token
            displayMessage('Token refreshed successfully!');
        } else {
            // Error message already displayed by apiCall, or if refresh failed & tokens cleared
            displayMessage('Failed to refresh token. Please login again.', true);
            clearTokens(); // Ensure tokens are cleared if refresh fails
        }
    });

    fetchProtectedButton.addEventListener('click', async () => {
        clearMessage();
        protectedDataOutput.textContent = 'Fetching...';
        const data = await apiCall('/protected', 'GET', null, true);
        if (data) {
            protectedDataOutput.textContent = JSON.stringify(data, null, 2);
            // If you expect a specific field, e.g., data.user_info:
            // protectedDataOutput.textContent = data.msg || JSON.stringify(data.user_info);
        } else {
            protectedDataOutput.textContent = 'Failed to fetch protected data.';
        }
    });
});
