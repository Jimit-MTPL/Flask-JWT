import unittest
import json
from app import create_app
from app.db_setup import db
from app.models import User, TokenBlacklist # Assuming TokenBlacklist might be needed for some tests

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key", # Consistent secret key for tests
            "WTF_CSRF_ENABLED": False # Disable CSRF for simpler form testing if applicable
        })
        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Helper to register a user
        self.test_user_email = "test@example.com"
        self.test_user_password = "password123"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _register_user(self, email, password):
        return self.client.post('/signup', data=json.dumps({
            "email": email,
            "password": password
        }), content_type='application/json')

    def _login_user(self, email, password):
        return self.client.post('/login', data=json.dumps({
            "email": email,
            "password": password
        }), content_type='application/json')

    # --- Test Cases ---

    def test_01_signup_success(self):
        """Test user signup with new email."""
        response = self._register_user(self.test_user_email, self.test_user_password)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], "User created successfully")
        # Check user in db
        user = User.query.filter_by(email=self.test_user_email).first()
        self.assertIsNotNone(user)

    def test_02_signup_existing_email(self):
        """Test user signup with an existing email."""
        self._register_user(self.test_user_email, self.test_user_password) # First registration
        response = self._register_user(self.test_user_email, "anotherpassword") # Second attempt
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], "User already exists")

    def test_03_login_success(self):
        """Test user login with correct credentials."""
        self._register_user(self.test_user_email, self.test_user_password)
        response = self._login_user(self.test_user_email, self.test_user_password)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    def test_04_login_wrong_email(self):
        """Test user login with a non-existent email."""
        self._register_user(self.test_user_email, self.test_user_password)
        response = self._login_user("wrong@example.com", self.test_user_password)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], "Bad email or password")

    def test_05_login_wrong_password(self):
        """Test user login with an incorrect password."""
        self._register_user(self.test_user_email, self.test_user_password)
        response = self._login_user(self.test_user_email, "wrongpassword")
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], "Bad email or password")

    def test_06_protected_route_no_token(self):
        """Test accessing a protected route without a token."""
        response = self.client.get('/protected')
        self.assertEqual(response.status_code, 401) # Expecting unauthorized

    def test_07_protected_route_with_token(self):
        """Test accessing a protected route with a valid token."""
        self._register_user(self.test_user_email, self.test_user_password)
        login_response = self._login_user(self.test_user_email, self.test_user_password)
        access_token = json.loads(login_response.data)['access_token']

        response = self.client.get('/protected', headers={
            "Authorization": f"Bearer {access_token}"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], "This is a protected route")

    def test_08_logout_and_blacklist(self):
        """Test token blacklisting on logout."""
        self._register_user(self.test_user_email, self.test_user_password)
        login_response = self._login_user(self.test_user_email, self.test_user_password)
        access_token = json.loads(login_response.data)['access_token']

        # Logout
        logout_response = self.client.post('/logout', headers={
            "Authorization": f"Bearer {access_token}"
        })
        self.assertEqual(logout_response.status_code, 200)

        # Try accessing protected route with the logged-out token
        response = self.client.get('/protected', headers={
            "Authorization": f"Bearer {access_token}"
        })
        self.assertEqual(response.status_code, 401) # Expecting unauthorized as token is blacklisted
        # Check if the JTI is in the TokenBlacklist table
        # This requires parsing the JWT to get JTI, which is more involved for a unit test here.
        # For now, we rely on the 401 from the protected route.
        # A more direct test would be to query TokenBlacklist table if JTI was accessible.

    def test_09_refresh_token_success(self):
        """Test successfully obtaining a new access token using a refresh token."""
        self._register_user(self.test_user_email, self.test_user_password)
        login_response = self._login_user(self.test_user_email, self.test_user_password)
        refresh_token = json.loads(login_response.data)['refresh_token']

        response = self.client.post('/refresh', headers={
            "Authorization": f"Bearer {refresh_token}"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)

    def test_10_refresh_with_access_token_fail(self):
        """Test attempting to use an access token to refresh (should fail)."""
        self._register_user(self.test_user_email, self.test_user_password)
        login_response = self._login_user(self.test_user_email, self.test_user_password)
        access_token = json.loads(login_response.data)['access_token']

        response = self.client.post('/refresh', headers={
            "Authorization": f"Bearer {access_token}" # Using access token here
        })
        self.assertEqual(response.status_code, 422) # Expect 422 as flask-jwt-extended identifies wrong token type

if __name__ == '__main__':
    unittest.main()
