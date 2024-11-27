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
    # Tokenize the input along with the conversation history
    new_user_input_ids = tokenizer.encode(
        user_input + tokenizer.eos_token, return_tensors="pt"
    )
    bot_input_ids = (
        torch.cat([conversation_history, new_user_input_ids], dim=-1)
        if conversation_history is not None
        else new_user_input_ids
    )

    # Generate a response
    conversation_history = model.generate(
        bot_input_ids,
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
        top_p=0.92,
        top_k=50,
    )
    bot_response = tokenizer.decode(
        conversation_history[:, bot_input_ids.shape[-1] :][0], skip_special_tokens=True
    )
    return bot_response, conversation_history


# Seller dashboard
def seller_dashboard():
    st.title("Seller Dashboard")
    st.write("Add your products and view their reviews:")
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

    for product_id in st.session_state["accounts"][st.session_state["current_user"]]["products"]:
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
    product_list = list(st.session_state["product_reviews"].keys())
    if not product_list:
        st.write("No products available at the moment.")
        return

    product_id = st.selectbox("Select a Product", product_list)
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

    # Chatbot Section
    st.subheader("Ask Assistify")
    user_input = st.text_input("Your message to the chatbot:")
    if st.button("Send to Chatbot"):
        if user_input.strip():
            prev_conversation = (
                st.session_state["conversation_history"][-1]
                if st.session_state["conversation_history"]
                else None
            )
            bot_response, updated_history = chatbot_response(user_input, prev_conversation)
            st.session_state["conversation_history"].append(updated_history)
            st.write(f"**Assistify:** {bot_response}")
        else:
            st.warning("Please enter a message.")


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
    st.sidebar.button("Sign Out", on_click=lambda: log_out())
    if st.session_state["user_role"] == "customer":
        customer_ui()
    elif st.session_state["user_role"] == "seller":
        seller_dashboard()
    elif st.session_state["user_role"] == "developer":
        developer_dashboard()
