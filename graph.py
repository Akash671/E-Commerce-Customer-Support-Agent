"""

"""


from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages



from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import Tool

from tools import (
    track_order,
    cancel_order,
    refund_status,
    recommend_products,
    escalate_to_human
)

import os 
from dotenv import load_dotenv

load_dotenv()


#===========
# MCP STATE
#===========


class AgentState(TypedDict):
    messages: Annotated[list,add_messages]
    user_query:str
    tool_result:str


#====================
# GEMINI MODEL(LLM)
#====================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)




#=====================
# REGISTER TOOLS
#=====================


# Tools Registry..
Tools = {
    "track_order": track_order,
    "cancel_order": cancel_order,
    "refund_status": refund_status,
    "recommend_products": recommend_products,
    "escalate_to_human": escalate_to_human
}



#======================
# MCP ROUTER NODE (or think this is MCP SERVICE)
#======================


def router_node(state:AgentState):
    """
    MCP Router:
    Decide which tool to call
    """

    query = state["user_query"].lower()
    if "track" in query and "order" in query:
        print("Debug: Routing to track order node...")
        return {"next": "track_order_node"}
    elif "cancel" in query:
        print("Debug: Routing to cancel order node...")
        return {"next": "cancel_order_node"}
    elif "refund" in query:
        print("Debug: Routing to refund node...")
        return {"next": "refund_node"}
    elif "recommend" in query or "suggest" in query:
        print("Debug: Routing to recommend node...")
        return {"next": "recommend_node"}
    else:
        print("Debug: Routing to human support node...")
        return {"next": "human_support_node"}
#==========================
# TOOL NODES 
#==========================


def track_order_node(state:AgentState):
    print("Debug: Inside track order node...")
    query = state["user_query"]
    order_id = extract_order_id(query)
    print(f"Extracted order id: {order_id}")
    result = track_order.invoke(order_id)  # tool execution

    print(f"Tool result: {result}")


    print("Debug: Track order node completed.")
    return {
        "tool_result": result,
        "messages": [HumanMessage(content=result)]
    }




def cancel_order_node(state:AgentState):
    print("Debug: Inside cancel order node...")
    query = state["user_query"]
    order_id = extract_order_id(query)
    print(f"Extracted order id: {order_id}")
    result = cancel_order.invoke(order_id) # tool execution
    print(f"Tool result: {result}")

    print("Debug: Cancel order node completed.")
    return {
        "tool_result": result,
        "messages": [HumanMessage(content=result)]
    }

def refund_node(state:AgentState):
    print("Debug: Inside refund node...")
    query = state["user_query"]
    order_id = extract_order_id(query)
    print(f"Extracted order id: {order_id}")
    result = refund_status.invoke(order_id)  # tool execution
    print(f"Tool result: {result}") 

    print("Debug: Refund node completed.")

    return {
        "tool_result": result,
        "messages": [HumanMessage(content=result)]
    }

def recommend_node(state:AgentState):
    print("Debug: Inside recommend node...")
    result = recommend_products.invoke("general") # tool execution

    print(f"Tool result: {result}")
    print("Debug: Recommend node completed.")
    return {
        "tool_result": result,
        "messages": [HumanMessage(content=result)]
    }

def human_support_node(state:AgentState):
    print("Debug: Inside human support node...")
    result = escalate_to_human.invoke(state["user_query"]) # tool execution

    print(f"Tool result: {result}")
    print("Debug: Human support node completed.")
    return {
        "tool_result": result,
        "messages": [HumanMessage(content=result)]
    }


#==========================
# RESPONSE GENERATOR NODE
#==========================


def response_node(state:AgentState):
    prompt = f"""
    You are a professional e-commerce customer support assistant.

    user query: {state['user_query']}
    tool result: {state['tool_result']}


    Generate a helpful customer-friendly response in natural language.
    """

    response = llm.invoke(prompt)

    return {
        "messages": [response]
    }

#========================
# HELPER NODES
#========================


def extract_order_id(text:str) -> str:
    print("Debug: Extracting order id node...")
    words = text.split()
    print("Extracting order id from query...")
    print(words)

    for word in words:
        if "ORD1" in word.upper():
            print(word.upper())
            return word.upper()
    print("extract_order_id node completed.")
    return "ORD1001"



#========================
# BUILD GRAPH
#========================



builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("track_order_node", track_order_node)
builder.add_node("cancel_order_node", cancel_order_node)
builder.add_node("refund_node", refund_node)
builder.add_node("recommend_node", recommend_node)
builder.add_node("human_support_node", human_support_node)
builder.add_node("response_node", response_node)



# ENTRY

builder.set_entry_point("router")


# ROUTES

builder.add_conditional_edges(
    "router",
    lambda x: x['next'],
    {
        "track_order_node": "track_order_node",
        "cancel_order_node": "cancel_order_node",
        "refund_node": "refund_node",
        "recommend_node": "recommend_node",
        "human_support_node": "human_support_node"
    }
)


# add edges in graph from tool nodes to response node

builder.add_edge("track_order_node", "response_node")
builder.add_edge("cancel_order_node", "response_node")
builder.add_edge("refund_node", "response_node")
builder.add_edge("recommend_node", "response_node")
builder.add_edge("human_support_node", "response_node")



# END

builder.add_edge("response_node", END)


# GRAPH COMPILE

from IPython.display import Image, display

graph = builder.compile()

display(Image(data=graph.get_graph().draw_mermaid_png()))




