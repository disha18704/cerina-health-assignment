import uvicorn
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from backend.graph import get_graph
from backend.models import ReviewMetadata
from langchain_core.messages import HumanMessage
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSqliteSaver.from_conn_string("backend/checkpoints.db") as checkpointer:
        app.state.graph = get_graph().compile(checkpointer=checkpointer)
        yield


app = FastAPI(title="Cerina Protocol Foundry API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    message: str
    thread_id: str

class ApprovalData(BaseModel):
    thread_id: str
    edited_content: Optional[str] = None


@app.post("/stream")
async def stream_workflow(data: RequestData):
    """Stream the workflow execution with real-time updates"""
    graph = app.state.graph
    config = {"configurable": {"thread_id": data.thread_id}}
    
    # Check if this is a new conversation
    current_state = await graph.aget_state(config)
    
    if not current_state.values:
        # Initialize new state
        inputs = {
            "messages": [HumanMessage(content=data.message)],
            "current_draft": None,
            "draft_history": [],
            "critiques": [],
            "scratchpad": [],
            "metadata": ReviewMetadata(),
            "last_reviewer": None
        }
    else:
        # Continue existing conversation
        inputs = {"messages": [HumanMessage(content=data.message)]}
    
    async def generate():
        """Generator for streaming events"""
        try:
            async for event in graph.astream(inputs, config=config):
                # Send each event as JSON
                yield f"data: {json.dumps(event, default=str)}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/state/{thread_id}")
async def get_state(thread_id: str):
    """Get current state for a thread"""
    graph = app.state.graph
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.aget_state(config)
    
    if not state.values:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Convert state to JSON-serializable format
    return {
        "current_draft": state.values.get("current_draft"),
        "draft_history": state.values.get("draft_history", []),
        "critiques": state.values.get("critiques", []),
        "scratchpad": state.values.get("scratchpad", []),
        "metadata": state.values.get("metadata"),
        "last_reviewer": state.values.get("last_reviewer"),
        "next_worker": state.values.get("next_worker")
    }


@app.post("/approve")
async def approve_draft(data: ApprovalData):
    """Approve and finalize a draft, optionally with edits"""
    graph = app.state.graph
    config = {"configurable": {"thread_id": data.thread_id}}
    
    # Get current state
    current_state = await graph.aget_state(config)
    if not current_state.values:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # If edited content provided, update the draft
    if data.edited_content:
        # Update the draft with edited content
        draft = current_state.values.get("current_draft")
        if draft:
            draft.content = data.edited_content
            # Resume with updated draft
            result = await graph.ainvoke(
                {"current_draft": draft},
                config=config
            )
        else:
            raise HTTPException(status_code=400, detail="No draft to edit")
    else:
        # Just approve - return final state
        result = current_state.values
    
    return {
        "status": "approved",
        "draft": result.get("current_draft"),
        "metadata": result.get("metadata")
    }


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Cerina Protocol Foundry API",
        "endpoints": {
            "POST /stream": "Stream workflow execution",
            "GET /state/{thread_id}": "Get current state",
            "POST /approve": "Approve draft with optional edits"
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
