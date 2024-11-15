import streamlit as st
import requests
import webbrowser

BASE_URL = "http://localhost:5000"

def signup():
    st.title("Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    response = None
    if st.button("Sign Up"):
        response = requests.post(f"{BASE_URL}/signup", json={"email": email, "password": password})
        if response:
            st.success("Registered Successfuly!")
        else:
            st.error("User already exists")

def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state['token'] = token 
            st.success("Login successful!")
            #st.write("Access Token:", token)
        else:
            st.write(response.json())

def google_login():
    st.title("Google Login")
    if st.button("Login with Google"):
        # Opens Google login in a new tab
        webbrowser.open(f"{BASE_URL}/login/google")           

def logout():
    if 'token' in st.session_state:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.post(f"{BASE_URL}/logout", headers=headers)
        if response.status_code == 200:
            st.session_state.pop("token", None)  # Remove token from session state
            st.success("Logout successful!")
        else:
            st.error("Logout failed.")

def check_login():
    if 'token' in st.session_state:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.get(f"{BASE_URL}/check_login", headers=headers)
        if response.status_code == 200:
            st.success("You are logged in!")
        else:
            st.error("You are logged out!")
    else:
        st.warning("You are logged out please login first!!")

# Streamlit navigation
st.sidebar.title("Navigation")
option = st.sidebar.radio("Choose Action", ["Sign Up", "Login", "Google Login", "Check Login", "Logout"])

if option == "Sign Up":
    signup()
elif option == "Login":
    login()
elif option == "Google Login":
    google_login()
elif option == "Check Login":
    check_login()
elif option == "Logout":
    logout()
    #if 'token' not in st.session_state:
    #   st.success("You are logged out.")