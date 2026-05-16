"""
author : @akash
"""

import streamlit as st
from graph import graph

# Streamlit page config
st.set_page_config(
    page_title="E-Commerce Assistant",
    page_icon="🛍️"
)

st.title("🛍️ E-Commerce Customer Support")
st.caption("Ask me about orders, returns, or product details!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
if user_query := st.chat_input("How can I help you today?"):

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generate assistant response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:
                # Initialize graph state
                state = {
                    "messages": [],
                    "user_query": user_query,
                    "tool_result": ""
                }

                # Invoke graph
                result = graph.invoke(state)

                # Extract response
                if result.get("messages"):
                    agent_response = result["messages"][-1].content
                else:
                    agent_response = "No response generated."

                # Display response
                st.markdown(agent_response)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": agent_response
                })

            except Exception as e:
                st.error(f"Error: {str(e)}")