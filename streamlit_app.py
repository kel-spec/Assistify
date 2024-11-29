import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Initialize session state variables
if "accounts" not in st.session_state:
    st.session_state["accounts"] = {
        "developer": {"password": "dev123", "role": "developer", "products": []}
    }

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if "product_reviews" not in st.session_state:
    st.session_state["product_reviews"] = {}

if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

# Load pretrained chatbot model
@st.cache_resource
def load_chatbot_model():
    model_name = "microsoft/DialoGPT-medium"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_chatbot_model()

# Chatbot functionality
def chatbot_response(user_input, conversation_history):
    new_user_input_ids = tokenizer.encode(
        user_input + tokenizer.eos_token, return_tensors="pt"
    )
    bot_input_ids = (
        torch.cat([conversation_history, new_user_input_ids], dim=-1)
        if conversation_history is not None
        else new_user_input_ids
    )
    conversation_history = model.generate(
        bot_input_ids,
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
        top_p=0.92,
        top_k=50,
    )
    bot_response = tokenizer.decode(
        conversation_history[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True
    )
    return bot_response, conversation_history

# Sign Up Function
def sign_up(username, password, role, products):
    if username in st.session_state["accounts"]:
        st.error("Username already exists.")
    else:
        st.session_state["accounts"][username] = {
            "password": password,
            "role": role,
            "products": products,
        }
        st.success(f"Account created successfully for {username}!")

# Sign In Function
def sign_in(username, password):
    if username in st.session_state["accounts"]:
        if st.session_state["accounts"][username]["password"] == password:
            st.session_state["current_user"] = username
            st.session_state["user_role"] = st.session_state["accounts"][username]["role"]
            st.success(f"Welcome back, {username}!")
        else:
            st.error("Incorrect password. Please try again.")
    else:
        st.error("Account not found. Please sign up.")

# Log Out Function
def log_out():
    st.session_state["current_user"] = None
    st.session_state["user_role"] = None
    st.success("You have successfully logged out.")

# Seller dashboard
def seller_dashboard():
    st.title("Seller Dashboard")
    new_product = st.text_input("Add a new product", "")
    if st.button("Add Product"):
        if new_product.strip():
            if new_product not in st.session_state["product_reviews"]:
                st.session_state["product_reviews"][new_product] = {"positive": [], "neutral": [], "negative": []}
            if new_product not in st.session_state["accounts"][st.session_state["current_user"]]["products"]:
                st.session_state["accounts"][st.session_state["current_user"]]["products"].append(new_product)
                st.success(f"Product '{new_product}' added successfully!")
            else:
                st.warning("Product already exists!")
        else:
            st.warning("Please enter a valid product name.")

# Customer interface
def customer_ui():
    st.title("Product Page")
    product_list = list(st.session_state["product_reviews"].keys())
    if not product_list:
        st.write("No products available at the moment.")
        return
    product_id = st.selectbox("Select a Product", product_list)
    if product_id:
        review_type = st.radio("Rate the product", ["1 - Negative", "2 - Neutral", "3 - Positive"])
        user_review = st.text_area("Write your review here (optional)")
        if st.button("Submit Review"):
            if "1" in review_type:
                st.session_state["product_reviews"][product_id]["negative"].append(user_review or "No detailed feedback")
            elif "2" in review_type:
                st.session_state["product_reviews"][product_id]["neutral"].append(user_review or "No detailed feedback")
            elif "3" in review_type:
                st.session_state["product_reviews"][product_id]["positive"].append(user_review or "No detailed feedback")
            st.success("Thank you for your feedback!")

# Developer interface
def developer_dashboard():
    st.title("Developer Dashboard")
    st.json(st.session_state)

# Sign-Up Page
def sign_up_page():
    st.header("Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", options=["customer", "seller"])
    products = []
    if role == "seller":
        products = st.text_area("List your products (comma-separated)").split(",")
    if st.button("Sign Up"):
        sign_up(username, password, role, products)

# Login Page
def login_page():
    st.header("Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign In"):
        sign_in(username, password)

# Main App Logic
if not st.session_state["current_user"]:
    st.sidebar.title("Welcome")
    action = st.sidebar.radio("Choose an action", ["Sign In", "Sign Up"])
    if action == "Sign In":
        login_page()
    elif action == "Sign Up":
        sign_up_page()
else:
    st.sidebar.title(f"Hello, {st.session_state['current_user']}")
    if st.sidebar.button("Sign Out"):
        log_out()
    if st.session_state["user_role"] == "customer":
        customer_ui()
    elif st.session_state["user_role"] == "seller":
        seller_dashboard()
    elif st.session_state["user_role"] == "developer":
        developer_dashboard()
