import streamlit as st

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
    st.session_state["product_reviews"] = {}  # Format: {"product_id": {"positive": [], "neutral": [], "negative": []}}


# Functions for authentication and account management
def sign_up(username, password, role, products=None):
    if username in st.session_state["accounts"]:
        st.warning("Username already exists!")
    else:
        st.session_state["accounts"][username] = {
            "password": password,
            "role": role,
            "products": products if role == "seller" else []
        }
        st.success("Account created successfully!")


def sign_in(username, password):
    account = st.session_state["accounts"].get(username)
    if account and account["password"] == password:
        st.session_state["current_user"] = username
        st.session_state["user_role"] = account["role"]
        st.session_state["products"] = account.get("products", [])
        st.success(f"Welcome back, {username}!")
    else:
        st.error("Invalid username or password.")


def log_out():
    st.session_state["current_user"] = None
    st.session_state["user_role"] = None
    st.session_state["products"] = []


# Seller dashboard
def seller_dashboard():
    st.title("Seller Dashboard")
    st.write("Here are your products and their reviews:")
    for product_id in st.session_state["products"]:
        st.subheader(f"Product: {product_id}")
        reviews = st.session_state["product_reviews"].get(product_id, {"positive": [], "neutral": [], "negative": []})
        st.write("### Positive Reviews")
        for review in reviews["positive"]:
            st.write(f"- {review}")
        st.write("### Neutral Reviews")
        for review in reviews["neutral"]:
            st.write(f"- {review}")
        st.write("### Negative Reviews")
        for review in reviews["negative"]:
            st.write(f"- {review}")


# Customer interface
def customer_ui():
    st.title("Product Page")
    product_id = st.selectbox("Select a Product", list(st.session_state["product_reviews"].keys()))
    if product_id:
        review_type = st.radio("Rate the product", options=["1 - Negative", "2 - Neutral", "3 - Positive"])
        user_review = st.text_area("Write your review here (optional)")

        if st.button("Submit Review"):
            if product_id in st.session_state["product_reviews"]:
                if "1" in review_type:
                    st.session_state["product_reviews"][product_id]["negative"].append(user_review or "No detailed feedback")
                elif "2" in review_type:
                    st.session_state["product_reviews"][product_id]["neutral"].append(user_review or "No detailed feedback")
                elif "3" in review_type:
                    st.session_state["product_reviews"][product_id]["positive"].append(user_review or "No detailed feedback")
                st.success("Thank you for your feedback!")
            else:
                st.error("Product not found.")


# Developer interface
def developer_dashboard():
    st.title("Developer Dashboard")
    st.write("### Registered Accounts")
    for user, details in st.session_state["accounts"].items():
        st.write(f"**{user}** - Role: {details['role']}, Products: {details.get('products', [])}")
    st.write("### App Settings")
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
    action = st.sidebar.radio("Choose an action", options=["Sign In", "Sign Up"])
    if action == "Sign In":
        login_page()
    elif action == "Sign Up":
        sign_up_page()
else:
    st.sidebar.title(f"Hello, {st.session_state['current_user']}")
    st.sidebar.button("Sign Out", on_click=log_out)
    if st.session_state["user_role"] == "customer":
        customer_ui()
    elif st.session_state["user_role"] == "seller":
        seller_dashboard()
    elif st.session_state["user_role"] == "developer":
        developer_dashboard()
