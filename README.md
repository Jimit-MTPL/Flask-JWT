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

## Project Structure

```
.
├── app/                  # Main application module
│   ├── __init__.py       # Application factory, Flask app setup
│   ├── auth.py           # Authentication logic (signup, login, JWT callbacks)
│   ├── db_setup.py       # Database setup and initialization
│   ├── models.py         # SQLAlchemy database models (User, TokenBlacklist)
│   └── routes.py         # API routes definition
├── tests/                # Unit tests
│   └── test_auth.py      # Authentication tests
├── .env.example          # Example environment variables file
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Copy the `.env.example` file to a new file named `.env`:
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file and provide actual values for the variables. See the "Environment Variables" section below for details.

5.  **Initialize the database:**
    (The application is currently set to create database tables automatically on startup if they don't exist. For production, you might want to use migrations like Flask-Migrate.)

## Running the Application

To run the Flask development server:

```bash
flask run
```

Or, if you have a `run.py` or similar entry point (not provided in this project structure, assuming direct Flask CLI usage):

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

-   **`GET /login/google`**: Initiates Google OAuth login. Redirects to Google's authentication page.
-   (Callback URL for Google OAuth is handled by Flask-Dance, usually `/login/google/authorized`)

## Environment Variables

The application requires several environment variables to be set for proper configuration, especially for security and third-party integrations. These should be defined in a `.env` file in the project root.

Refer to the `.env.example` file for a template.

Key variables include:

-   `FLASK_SECRET_KEY`: A secret key for Flask application sessions and other security-related features (e.g., CSRF protection if used).
-   `JWT_SECRET_KEY`: The secret key used to sign and verify JWTs. This should be a strong, random string.
-   `DATABASE_URL`: The connection string for the SQLAlchemy database.
    -   Example for PostgreSQL: `postgresql://user:password@host:port/database`
    -   Example for SQLite (local development): `sqlite:///./instance/app.db`
-   `GOOGLE_OAUTH_CLIENT_ID`: Your Google OAuth Client ID.
-   `GOOGLE_OAUTH_CLIENT_SECRET`: Your Google OAuth Client Secret.

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
