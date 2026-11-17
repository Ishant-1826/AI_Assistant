from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

from ..database import (
    create_session, get_sessions, get_session, update_session_title,
    delete_session, add_message, get_messages
)
from ..llm.assistant import stream_chat_response
from ..config import settings

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class MessageRequest(BaseModel):
    session_id: str
    message: str
    provider: Optional[str] = None
    api_key: Optional[str] = None
    web_search_enabled: Optional[bool] = False

class SessionTitleUpdate(BaseModel):
    title: str

@router.get("/sessions")
def list_sessions():
    return get_sessions()

@router.post("/sessions")
def new_session():
    return create_session("New Chat")

@router.get("/sessions/{session_id}")
def load_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = get_messages(session_id)
    return {"session": session, "messages": messages}

@router.patch("/sessions/{session_id}")
def rename_session(session_id: str, body: SessionTitleUpdate):
    success = update_session_title(session_id, body.title)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "title": body.title}

@router.delete("/sessions/{session_id}")
def remove_session(session_id: str):
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success"}

@router.post("/stream")
async def chat_stream_endpoint(req: MessageRequest):
    # Save user message to database
    add_message(session_id=req.session_id, role="user", content=req.message)
    
    # Retrieve conversation history
    history = get_messages(req.session_id)
    formatted_history = [{"role": m["role"], "content": m["content"]} for m in history]
    
    async def event_generator():
        accumulated_text = ""
        tool_data = None
        accumulated_sources = []
        accumulated_queries = []
        
        async for event in stream_chat_response(
            messages=formatted_history,
            provider=req.provider,
            api_key=req.api_key,
            web_search_enabled=req.web_search_enabled or False
        ):
            if event["type"] == "search_status":
                yield f"data: {json.dumps(event)}\n\n"
            elif event["type"] == "sources":
                accumulated_sources = event.get("sources", [])
                accumulated_queries = event.get("queries", [])
                yield f"data: {json.dumps(event)}\n\n"
            elif event["type"] == "tool":
                tool_data = event["tool_data"]
                yield f"data: {json.dumps(event)}\n\n"
            elif event["type"] in ("chunk", "info"):
                accumulated_text += event["text"]
                yield f"data: {json.dumps(event)}\n\n"
            elif event["type"] == "done":
                # Package tool_data and sources together if either exists
                saved_metadata = {}
                if tool_data:
                    saved_metadata["tool_data"] = tool_data
                if accumulated_sources:
                    saved_metadata["sources"] = accumulated_sources
                    saved_metadata["queries"] = accumulated_queries
                    
                # Save assistant response to DB
                add_message(
                    session_id=req.session_id,
                    role="assistant",
                    content=accumulated_text,
                    tool_data=saved_metadata if saved_metadata else None
                )
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/config")
def get_llm_status():
    return {
        "gemini_configured": bool(settings.gemini_api_key),
        "openai_configured": bool(settings.openai_api_key),
        "default_provider": settings.default_llm_provider,
        "gemini_model": settings.model_name_gemini,
        "openai_model": settings.model_name_openai
    }
