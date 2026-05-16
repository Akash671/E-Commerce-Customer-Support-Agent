"""
author : @akash
"""


import streamlit as st
import requests
#import os

# Configure the backend URL (Fallback to local if env variable isn't set)
BACKEND_URL = "http://localhost:8000"
#"http://localhost:8080"

#BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

st.set_page_config(page_title="E-Commerce Assistant", page_icon="🛍️")
st.title("🛍️ E-Commerce Customer Support")
st.caption("Ask me about orders, returns, or product details!")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new user input
if user_query := st.chat_input("How can I help you today?"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Call FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"user_query": user_query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    agent_response = response.json()["response"]
                    st.markdown(agent_response)
                    st.session_state.messages.append({"role": "assistant", "content": agent_response})
                else:
                    st.error(f"Backend Error: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend server. Is it running?")
