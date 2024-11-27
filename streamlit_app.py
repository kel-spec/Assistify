import streamlit as st
from textblob import TextBlob
import random

# Initialize account database in session state
if "accounts" not in st.session_state:
    st.session_state["accounts"] = {"developer": {"password": "dev123", "role": "developer"}}
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

# Function to validate login
def validate_login(username, password):
    accounts = st.session_state["accounts"]
    if username in accounts and accounts[username]["password"] == password:
        return accounts[username]["role"]
    return None

# Function to detect sentiment with intensity
def detect_sentiment_intensity(message):
    analysis = TextBlob(message)
    polarity = analysis.sentiment.polarity
    if polarity > 0.5:
        return "strongly positive"
    elif polarity > 0:
        return "mildly positive"
    elif polarity < -0.5:
        return "strongly negative"
    elif polarity < 0:
        return "mildly negative"
    else:
        return "neutral"

# Define responses with emojis for each sentiment intensity
responses = {
    "strongly positive": ["That's fantastic! 😊 We’re thrilled you’re happy with our product."],
    "mildly positive": ["Thanks for your feedback! 😊 Glad to know you’re satisfied."],
    "neutral": ["Thanks for reaching out. 😊 Let us know if you have any questions!"],
    "mildly negative": ["We apologize if things didn’t meet your expectations. 😟 How can we help?"],
    "strongly negative": ["We’re really sorry to hear that. 😞 Please contact support, and we’ll assist you immediately."],
}

# Login or signup screen
if st.session_state["user_role"] is None:
    st.title("Welcome to Assistify 🛒")
    st.subheader("Sign in or Sign up to continue")
    
    # Login form
    with st.form("login_form"):
        st.write("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Sign In")
    
    if submit_login:
        role = validate_login(username, password)
        if role:
            st.session_state["user_role"] = role
            st.session_state["current_user"] = username
            st.success(f"Welcome back, {username}!")
        else:
            st.error("Invalid username or password.")
    
    # Signup form
    st.write("---")
    with st.form("signup_form"):
        st.write("Sign Up")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_signup = st.form_submit_button("Sign Up")
    
    if submit_signup:
        if new_password != confirm_password:
            st.error("Passwords do not match!")
        elif new_username in st.session_state["accounts"]:
            st.error("Username already exists!")
        else:
            st.session_state["accounts"][new_username] = {"password": new_password, "role": "customer"}
            st.success("Account created successfully! Please log in.")

# Customer interface
elif st.session_state["user_role"] == "customer":
    st.title(f"Welcome, {st.session_state['current_user']}!")
    st.sidebar.header("Customer Settings")
    
    # Product display
    st.subheader("Product: Wireless Earbuds")
    st.image("https://via.placeholder.com/150", caption="Wireless Earbuds", use_column_width=True)

    # Star-based review system
    st.subheader("Leave a Quick Review")
    rating = st.radio("Rate the product:", [1, 2, 3], format_func=lambda x: f"{x} Star{'s' if x > 1 else ''}")
    if st.button("Submit Star Review"):
        st.success("Thank you for your feedback!")
    
    st.write("---")
    st.subheader("Have More to Say? Chat With Us!")
    user_input = st.text_input("You:", "")
    if st.button("Send Chat Review"):
        st.success("Thank you for your detailed feedback!")

    if st.button("Sign Out"):
        st.session_state["user_role"] = None

# Seller interface
elif st.session_state["user_role"] == "seller":
    st.title(f"Seller Dashboard - {st.session_state['current_user']}")
    st.sidebar.header("Seller Settings")
    
    st.write("Review summary will be displayed here.")
    if st.button("Sign Out"):
        st.session_state["user_role"] = None

# Developer interface
elif st.session_state["user_role"] == "developer":
    st.title("Developer Dashboard")
    st.sidebar.header("Developer Settings")
    
    # Manage accounts
    st.subheader("Accounts Database")
    for user, info in st.session_state["accounts"].items():
        st.write(f"Username: {user}, Role: {info['role']}")
    
    if st.button("Sign Out"):
        st.session_state["user_role"] = None
