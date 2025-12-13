import operator
from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from backend.models import ExerciseDraft, Critique, AgentNote, DraftVersion, ReviewMetadata

class AgentState(TypedDict):
    # Core messaging
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Enhanced draft tracking
    current_draft: Optional[ExerciseDraft]
    draft_history: Annotated[List[DraftVersion], operator.add]
    
    # Rich feedback system
    critiques: Annotated[List[Critique], operator.add]
    scratchpad: Annotated[List[AgentNote], operator.add]
    
    # Metadata tracking
    metadata: ReviewMetadata
    
    # Routing control
    next_worker: Optional[str]
    last_reviewer: Optional[str]  # Track who reviewed last for proper re-review cycles
