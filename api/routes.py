from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from agent.graph import agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    system_prompt: str = "Tu es un assistant utile et concis."


class ChatResponse(BaseModel):
    response: str
    history: list[dict]


def build_messages(request: ChatRequest):
    messages = [SystemMessage(content=request.system_prompt)]

    for msg in request.history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=request.message))
    return messages


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        messages = build_messages(request)
        result = await agent.ainvoke({"messages": messages})

        response_text = result["messages"][-1].content

        new_history = request.history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": response_text}
        ]

        return ChatResponse(response=response_text, history=new_history)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi.responses import StreamingResponse
import json


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    messages = build_messages(request)

    async def event_generator():
        async for event in agent.astream_events(
                {"messages": messages}, version="v2"
        ):
            kind = event["event"]


            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    yield f"data: {json.dumps({'token': chunk})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")