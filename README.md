# Flask JWT Authentication App

A Flask-based web application demonstrating user authentication with JWT (JSON Web Tokens), including signup, login, logout (token blacklisting), and token refresh functionalities. It also integrates Google OAuth for social login.

## Features

- User registration and login
- JWT-based authentication (access and refresh tokens)
- Token blacklisting on logout
- Refresh token mechanism
- Protected routes
- Google OAuth integration
- Configuration via environment variables
- Basic logging
- Unit tests
- Basic web frontend for API interaction

## Prerequisites

Before you begin, ensure you have the following installed:

-   **Python**: Version 3.8 or higher is recommended. You can download it from [python.org](https://www.python.org/).
-   **pip**: The Python package installer (usually comes with Python).
-   **Virtual Environment Tool** (optional but highly recommended): Python's `venv` module (standard in Python 3) or `virtualenv`.
-   **Git**: For cloning the repository (optional if you download the source code as a ZIP file). You can get Git from [git-scm.com](https://git-scm.com/).
-   **Flask CLI**: This is part of the Flask installation (covered in the setup steps below) and is used for running the development server (`flask run`) and database initialization commands (`flask init-db`).

## Project Structure

```
.
├── app/                            # Main Flask application module
│   ├── __init__.py                 # Application factory, Flask app setup, CORS, CLI commands
│   ├── auth.py                     # Authentication logic (signup, login, JWT callbacks, etc.)
│   ├── db_setup.py                 # Database setup (SQLAlchemy instance and initialization)
│   ├── models.py                   # SQLAlchemy database models (User, TokenBlacklist)
│   └── routes.py                   # API endpoint definitions (Blueprints)
│
├── frontend/                       # Frontend applications
│   ├── streamlit_app.py            # Original Streamlit frontend (may be outdated or separate)
│   └── web-client/                 # Simple HTML/CSS/JS client for the auth API
│       ├── index.html              # HTML structure for the web client
│       ├── style.css               # CSS styles for the web client
│       └── script.js               # JavaScript logic for interacting with the API
│
├── tests/                          # Unit and integration tests
│   └── test_auth.py                # Authentication related tests
│
├── .env.example                    # Example template for environment variables
├── .gitignore                      # Specifies intentionally untracked files that Git should ignore
├── README.md                       # This project documentation file
└── requirements.txt                # Python package dependencies for the backend
```

## Setup

1.  **Clone the Repository:**
    If you have Git installed, clone the repository from its source. Replace `<repository-url>` with the actual URL and `<project-directory>` with your desired local directory name.
    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```
    Alternatively, you can download the source code as a ZIP file and extract it.

2.  **Create and Activate a Virtual Environment:**
    Using a virtual environment is crucial for managing project-specific dependencies and avoiding conflicts with global Python packages.
    Navigate into your project directory, then create a virtual environment (e.g., named `venv`):
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    -   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows (Command Prompt/PowerShell):
        ```bash
        .\venv\Scripts\activate
        ```
    Your command prompt should now indicate that the virtual environment is active.

3.  **Install Dependencies:**
    With your virtual environment activated, install all the required Python packages listed in the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Environment variables are used to configure the application, especially for sensitive data like secret keys and database URLs.
    Copy the `.env.example` file to a new file named `.env` in the project root:
    ```bash
    cp .env.example .env
    ```
    Open the newly created `.env` file and provide actual, secure values for all the variables listed. Refer to the "Environment Variables" section below for detailed explanations of each variable, especially for Google OAuth setup.

    *Note on Flask-CORS*: This application includes `Flask-CORS` to handle Cross-Origin Resource Sharing. It's enabled by default in `app/__init__.py` which allows the web frontend (even if opened as a local `file:///` or served from a different port during development) to communicate with the API without common CORS errors.

5.  **Set Up Google OAuth 2.0 Credentials:**
    To use the "Login with Google" feature, you need to configure OAuth 2.0 credentials in the Google Cloud Console.
    -   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    -   Create a new project or select an existing one.
    -   Navigate to "APIs & Services" > "Credentials".
    -   Click "+ CREATE CREDENTIALS" and choose "OAuth client ID".
    -   Configure the OAuth consent screen if you haven't already. For "User Type", you can choose "External" for testing. Fill in the required app information. For scopes, you can leave it blank for now or add basic `email` and `profile` if needed later.
    -   For the "Application type", select "Web application".
    -   **Authorized JavaScript origins**: Add URIs like `http://127.0.0.1:5000` and `http://localhost:5000`. If you use a different port for your local Flask development server, add that too. If your frontend is served on a different port (e.g., by a live server extension), add that origin as well (e.g., `http://localhost:8080`).
    -   **Authorized redirect URIs**: This is critical. It must match the URI that Google will redirect to after successful authentication. For this application (using Flask-Dance), it's typically the path of your Google login route (`/login/google`) plus `/authorized`. So, if your app runs on `http://127.0.0.1:5000`, you should add:
        -   `http://127.0.0.1:5000/login/google/authorized`
        -   `http://localhost:5000/login/google/authorized` (it's good to have both `127.0.0.1` and `localhost`)
    -   Click "Create". You will be shown a "Client ID" and "Client secret".
    -   Copy these values and paste them into the `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` variables in your `.env` file.
    -   Ensure the "OAuth 2.0 API" (sometimes listed as "Google People API" or similar for profile info) is enabled in the "APIs & Services" > "Library" section for your project. Flask-Dance uses this to fetch user information.

    #### Note on HTTP for Local Development (`InsecureTransportError`)
    When running your Flask development server locally, it typically uses HTTP. Google OAuth 2.0, by default, requires HTTPS for all communications, and attempting to use it over HTTP will result in an `InsecureTransportError` from the `oauthlib` library used by Flask-Dance.

    For **local development and testing purposes only**, you can allow OAuth 2.0 to run over HTTP by setting the following environment variable in your `.env` file:
    ```
    OAUTHLIB_INSECURE_TRANSPORT="1"
    ```
    **IMPORTANT**: This setting **must not** be used in a production environment. In production, you must use HTTPS for all OAuth communications to ensure security. Remove this variable or set it to `"0"` in production.

6.  **Initialize the Database:**
    Once your environment variables (especially `DATABASE_URL`) are correctly set in your `.env` file, run the following command from the project root directory (with your virtual environment still active) to create the necessary database tables:
    ```bash
    flask init-db
    ```
    This command needs to be run once after setting up your `DATABASE_URL` environment variable.

## Running the Application

After completing all the setup steps:

1.  **Ensure your virtual environment is activated.** (Your command prompt should indicate this).
2.  **Ensure you are in the project root directory.**
3.  **(Optional but Recommended) Set `FLASK_APP` environment variable:**
    The Flask CLI needs to know where your application instance is. You can set this environment variable:
    -   On macOS and Linux:
        ```bash
        export FLASK_APP=app
        ```
    -   On Windows (Command Prompt):
        ```bash
        set FLASK_APP=app
        ```
    -   On Windows (PowerShell):
        ```bash
        $env:FLASK_APP = "app"
        ```
    (This tells Flask to look for the application factory `create_app` in the `app` package/directory. You can also set this in a `.flaskenv` file in your project root by adding the line `FLASK_APP=app`.)

4.  **Run the Flask development server:**
    ```bash
    flask run
    ```

Alternatively, if you were to use a `run.py` file (not included by default in this project, which uses the Flask CLI pattern):

```bash
python run.py
```

The application will typically be available at `http://127.0.0.1:5000/`.

## Authentication API

The authentication system uses JSON Web Tokens (JWTs). Upon successful login, the client receives an `access_token` and a `refresh_token`.

-   **Access Token**: Used to authenticate requests to protected endpoints. It is short-lived.
-   **Refresh Token**: Used to obtain a new access token when the current one expires. It is longer-lived.

### Endpoints:

All request and response bodies are in JSON format.

-   **`POST /signup`**: User registration.
    -   Request body: `{ "email": "user@example.com", "password": "yourpassword" }`
    -   Success response (201): `{ "msg": "User created successfully" }`
    -   Error response (400): `{ "msg": "User already exists" }`

-   **`POST /login`**: User login.
    -   Request body: `{ "email": "user@example.com", "password": "yourpassword" }`
    -   Success response (200): `{ "access_token": "...", "refresh_token": "..." }`
    -   Error response (401): `{ "msg": "Bad email or password" }`

-   **`POST /logout`**: User logout. Invalidates the current access token by adding its JTI (JWT ID) to a blacklist. Requires a valid access token in the `Authorization` header.
    -   Header: `Authorization: Bearer <access_token>`
    -   Success response (200): `{ "msg": "Successfully logged out" }`

-   **`POST /refresh`**: Obtain a new access token. Requires a valid refresh token in the `Authorization` header.
    -   Header: `Authorization: Bearer <refresh_token>`
    -   Success response (200): `{ "access_token": "..." }`
    -   Error response (401): If the refresh token is invalid or expired.

-   **`GET /protected`**: An example protected route. Requires a valid access token.
    -   Header: `Authorization: Bearer <access_token>`
    -   Success response (200): `{ "msg": "This is a protected route" }`
    -   Error response (401/422): If token is missing, invalid, or expired.

-   **`GET /login/google`**: Initiates the Google OAuth 2.0 login flow. This endpoint redirects the user to Google's authentication page.
    -   Upon successful authentication with Google, Google redirects the user back to the application's backend at a pre-configured "Authorized redirect URI" (e.g., `http://127.0.0.1:5000/login/google/authorized`, handled by Flask-Dance).
    -   The backend (`/login/google/authorized` route) then processes Google's callback, creates or logs in the user, and generates JWT access and refresh tokens.
    -   Finally, the backend redirects the user's browser to the `FRONTEND_URL` (which should point to `oauth_callback.html`, as defined in your `.env` file) with these tokens appended as query parameters (e.g., `/frontend/web-client/oauth_callback.html?access_token=...&refresh_token=...`).
    -   The `oauth_callback.html` page, using `callback_script.js`, extracts these tokens from the URL, stores them in `localStorage`, and then redirects to the main `index.html` page.

## Environment Variables

The application requires several environment variables to be set for proper configuration, especially for security and third-party integrations. These should be defined in a `.env` file in the project root.

Refer to the `.env.example` file for a template.

Key variables include:

-   `FLASK_SECRET_KEY`: A secret key for Flask application sessions and other security-related features (e.g., CSRF protection if used).
-   `JWT_SECRET_KEY`: The secret key used to sign and verify JWTs. This should be a strong, random string.
-   `DATABASE_URL`: The connection string for the SQLAlchemy database (e.g., `postgresql://user:password@host:port/database` or `sqlite:///./instance/app.db`).
-   `GOOGLE_OAUTH_CLIENT_ID`: Your Google OAuth 2.0 Client ID. Obtained from the Google Cloud Console. This is required for the "Login with Google" feature.
-   `GOOGLE_OAUTH_CLIENT_SECRET`: Your Google OAuth 2.0 Client Secret. Obtained from the Google Cloud Console. This is required for the "Login with Google" feature.
-   `FRONTEND_URL`: The URL to the frontend OAuth callback page (e.g., `/frontend/web-client/oauth_callback.html`). After successful Google authentication and backend processing, the user is redirected here by the backend with tokens in the URL query parameters. This page then saves the tokens and redirects to the main frontend page (e.g., `index.html`).
-   `OAUTHLIB_INSECURE_TRANSPORT`: Set to `"1"` to allow OAuth 2.0 to run over HTTP during local development for Google OAuth. **Crucial Warning**: This is for development/testing only. **Never use this setting in production.** Production environments must use HTTPS for OAuth.

## Running Tests

The project includes unit tests for the authentication system. To run the tests:

1.  Ensure you have installed development dependencies (if any, though `unittest` is standard).
2.  Navigate to the project root directory.
3.  Run the following command:

    ```bash
    python -m unittest discover -s tests -p "test_*.py"
    ```

    Alternatively, to run a specific test file:
    ```bash
    python -m unittest tests.test_auth
    ```

This command will discover and run all test cases found in files matching `test_*.py` within the `tests` directory.

## Web Frontend Client

A simple HTML, CSS, and JavaScript based web client is available in the `frontend/web-client/` directory. This client allows you to interact with the backend API for most authentication features.

### How to Use:

1.  **Ensure the Backend is Running**: The Flask backend application (typically on `http://127.0.0.1:5000/`) must be running.
2.  **Open `index.html`**: Navigate to the `frontend/web-client/` directory in your file explorer.
3.  Open the `index.html` file directly in your web browser (e.g., Chrome, Firefox, Safari, Edge).

### Functionality:

The web client provides a user interface to:
- Sign up a new user.
- Log in with existing credentials.
- Store access and refresh tokens in `localStorage`.
- Log out (which blacklists the access token on the backend).
- Refresh an access token using a refresh token.
- Fetch data from a protected API endpoint.
- Display API responses and error messages.
- Initiate login via Google using the "Login with Google" button. This redirects to the backend, which then goes through the Google OAuth flow.
- After returning from Google, the user is redirected by the backend to `oauth_callback.html` (with tokens in the URL). This page's script (`callback_script.js`) saves the tokens to `localStorage` and then redirects to `index.html`.
- The main `index.html` page (`script.js`) then uses these tokens from `localStorage` for subsequent authenticated actions.

### Important Notes:

-   **CORS (Cross-Origin Resource Sharing)**: The backend is configured with `Flask-CORS` to allow requests from different origins (e.g., if you open `index.html` directly or serve it via a local development server on a different port). The default configuration is permissive. The `script.js` file assumes the backend is at `http://127.0.0.1:5000`.
-   **Simplicity**: This client is for demonstration and testing purposes and lacks advanced features, styling, or production-ready error handling beyond basic messages.
