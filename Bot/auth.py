import streamlit as st
import json
import os
import requests
from streamlit_lottie import st_lottie

USER_CREDENTIALS_FILE = "users.json"

# -------------------- USER HANDLING --------------------
def load_users():
    if os.path.exists(USER_CREDENTIALS_FILE):
        with open(USER_CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    else:
        default_users = {"admin": "password123"}
        with open(USER_CREDENTIALS_FILE, "w") as f:
            json.dump(default_users, f)
        return default_users

def save_users(users_db):
    with open(USER_CREDENTIALS_FILE, "w") as f:
        json.dump(users_db, f, indent=2)

users_db = load_users()

# -------------------- STYLING --------------------
BASE_CSS = """
<style>
body {
    background: linear-gradient(135deg, #89f7fe, #66a6ff);
}
h1, h2, h3, label {
    color: black !important;
    text-align: center;
}

input, textarea {
    border-radius: 10px !important;
    padding: 0.6rem !important;
    border: 2px solid #ddd !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 0 rgba(0,0,0,0) !important;
}
input:hover, textarea:hover {
    border-color: #66a6ff !important;
    box-shadow: 0 4px 12px rgba(102, 166, 255, 0.4) !important;
    transform: translateY(-2px) !important;
}
input:focus, textarea:focus {
    border-color: #89f7fe !important;
    box-shadow: 0 4px 15px rgba(137, 247, 254, 0.6) !important;
    outline: none !important;
    transform: translateY(-2px) scale(1.02) !important;
}
.stButton > button {
    width: 100%;
    padding: 0.7rem;
    border-radius: 10px;
    font-weight: bold;
    border: none;
    background: linear-gradient(90deg, #66a6ff, #89f7fe);
    color: white;
    transition: 0.3s;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #89f7fe, #66a6ff);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
</style>
"""

# -------------------- ANIMATION LOADER --------------------
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

login_anim = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json")
signup_anim = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_zw0djhar.json")
welcome_anim = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_touohxv0.json") 

# -------------------- LOGIN PAGE --------------------
def login_page():
    st.set_page_config(page_title="Login", page_icon="🔑", layout="centered")
    st.markdown(BASE_CSS, unsafe_allow_html=True)

    # Welcome animation + title
    st_lottie(welcome_anim, height=200, key="welcome_login")
    st.markdown("<h1 style='text-align: center; color: black;'>👋 Welcome to <span style='color:#66a6ff;'>Cube AI Chatbot</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:18px;'>Your AI-powered assistant, ready to help you!</p>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card" style="padding:20px; border-radius:15px; background:white; box-shadow:0 4px 20px rgba(0,0,0,0.1);">', unsafe_allow_html=True)

        st_lottie(login_anim, height=160, key="login_anim")
        st.markdown("## 🔑 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login-btn"):
                if username in users_db and users_db[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        with col2:
            if st.button("Create Account", key="switch-to-signup"):
                st.session_state.show_signup = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- SIGNUP PAGE --------------------
def signup_page():
    st.set_page_config(page_title="Sign Up", page_icon="📝", layout="centered")
    st.markdown(BASE_CSS, unsafe_allow_html=True)

    # Welcome animation + title
    st_lottie(welcome_anim, height=200, key="welcome_signup")
    st.markdown("<h1 style='text-align: center; color: black;'>📝 Join <span style='color:#66a6ff;'>Cube AI Chatbot</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:18px;'>Create your account and start chatting instantly!</p>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card" style="padding:20px; border-radius:15px; background:white; box-shadow:0 4px 20px rgba(0,0,0,0.1);">', unsafe_allow_html=True)

        st_lottie(signup_anim, height=160, key="signup_anim")
        st.markdown("## 📝 Sign Up")

        new_username = st.text_input("Choose Username")
        new_password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign Up", key="signup-btn"):
                if not new_username or not new_password:
                    st.warning("⚠️ Please fill in all fields")
                elif new_username in users_db:
                    st.error("❌ Username already exists")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    users_db[new_username] = new_password
                    save_users(users_db)
                    st.success("🎉 Account created! Please login now.")
                    st.session_state.show_signup = False
                    st.rerun()
            if st.button("Back to Login", key="back-to-login"):
                st.session_state.show_signup = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- LOGOUT BUTTON --------------------
def logout_button():
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.messages = []
        st.session_state.chat_id = None
        st.rerun()

# -------------------- CONTROLLER --------------------
def auth_controller():
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False

    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
