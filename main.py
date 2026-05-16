"""
main.py file
"""


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import graph




app = FastAPI(title = "E-Commerce Customer Support Agent")


# define the request structure

class ChatRequest(BaseModel):
    user_query: str


# define the response structure

class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # initialize the langgraph state

        state={
            "messages" : [],
            "user_query" : request.user_query,
            "tool_result" : ""
        }

        # invoke the graph
        result = graph.invoke(state)

        if not result.get("messages"):
            raise HTTPException(status_Code = 500, detail = "no response from agent")
        final_message = result['messages'][-1].content
        return ChatResponse(response = final_message)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))