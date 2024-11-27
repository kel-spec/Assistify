import streamlit as st
from textblob import TextBlob
import random

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
    "strongly positive": ["That's fantastic! 😊 We’re thrilled you’re happy with our service."],
    "mildly positive": ["Thanks for your feedback! 😊 Glad to know you’re satisfied."],
    "neutral": ["Thanks for reaching out. 😊 Let us know if you have any questions!"],
    "mildly negative": ["We apologize if things didn’t meet your expectations. 😟 How can we help?"],
    "strongly negative": ["We’re really sorry to hear that. 😞 Please contact support, and we’ll assist you immediately."],
}

# Initialize session state for login
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if "reviews" not in st.session_state:
    st.session_state["reviews"] = {"positive": [], "neutral": [], "negative": []}

# User login selection
if st.session_state["user_role"] is None:
    st.title("Welcome to Assistify 🛒")
    st.subheader("Sign in as")
    if st.button("Customer"):
        st.session_state["user_role"] = "customer"
    elif st.button("Seller"):
        st.session_state["user_role"] = "seller"

# Customer interface
elif st.session_state["user_role"] == "customer":
    st.title("Assistify Chatbot - Customer")
    st.sidebar.header("Customer Settings")
    
    # Sample product display
    st.subheader("Available Products")
    st.write("1. Wireless Earbuds - $50")
    st.write("2. Smartwatch - $120")
    st.write("3. Bluetooth Speaker - $30")

    # Initialize conversation history
    if "conversation_history" not in st.session_state:
        st.session_state["conversation_history"] = []

    # Function to greet the user
    def greet_user(name):
        return f"Hello, {name}! How can I assist you today?"

    # User name input
    user_name = st.sidebar.text_input("Enter your name", "Guest")

    # Greet user if name provided
    if user_name:
        st.write(greet_user(user_name))

    # User message input
    user_input = st.text_input("You:", "")

    # Generate response on button click
    if st.button("Send"):
        if user_input.strip():
            sentiment = detect_sentiment_intensity(user_input)
            response = random.choice(responses.get(sentiment, ["I'm here to help!"]))
            st.session_state["conversation_history"].append({"user": user_input, "bot": response})
            # Save categorized reviews
            if sentiment in ["strongly positive", "mildly positive"]:
                st.session_state["reviews"]["positive"].append(user_input)
            elif sentiment == "neutral":
                st.session_state["reviews"]["neutral"].append(user_input)
            else:
                st.session_state["reviews"]["negative"].append(user_input)
        else:
            st.warning("Please enter a message.")

    # Display conversation history
    for turn in st.session_state["conversation_history"]:
        st.markdown(f"**You:** {turn['user']}")
        st.markdown(f"<div style='margin-left: 20px;'>Assistify: {turn['bot']}</div>", unsafe_allow_html=True)

# Seller interface
elif st.session_state["user_role"] == "seller":
    st.title("Assistify Dashboard - Seller")
    st.sidebar.header("Seller Settings")
    
    st.subheader("Customer Feedback Summary")
    st.write("### Positive Reviews")
    st.write(st.session_state["reviews"]["positive"] or "No positive reviews yet.")
    
    st.write("### Neutral Reviews")
    st.write(st.session_state["reviews"]["neutral"] or "No neutral reviews yet.")
    
    st.write("### Negative Reviews")
    st.write(st.session_state["reviews"]["negative"] or "No negative reviews yet.")

    st.write("Sign out if you wish to return to the startup window.")
    if st.button("Sign Out"):
        st.session_state["user_role"] = None
