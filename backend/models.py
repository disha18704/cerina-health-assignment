from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ExerciseDraft(BaseModel):
    title: str = Field(description="Title of the CBT exercise")
    content: str = Field(description="The full markdown content of the exercise")
    instructions: str = Field(description="Instructions for the patient")

class Critique(BaseModel):
    author: str = Field(description="Name of the agent (Safety or Clinical)")
    content: str = Field(description="The critique text")
    approved: bool = Field(description="Whether the draft is approved")

class SupervisorDecision(BaseModel):
    next_node: str = Field(description="The next worker node to call")
    reasoning: str = Field(description="Reasoning for the routing decision")

class AgentNote(BaseModel):
    """Scratchpad note from one agent to others"""
    author: str = Field(description="Agent who wrote this note")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    target: Optional[str] = Field(default=None, description="Which agent this is for")
    content: str = Field(description="The note content")
    priority: str = Field(default="info", description="Priority level: info, warning, critical")

class DraftVersion(BaseModel):
    """A version of the exercise draft"""
    version_number: int = Field(description="Version number")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    draft: ExerciseDraft = Field(description="The draft content")
    created_by: str = Field(description="Agent who created this version")
    notes: str = Field(description="Notes about this version")

class ReviewMetadata(BaseModel):
    """Metrics and scores for the review process"""
    safety_score: Optional[float] = Field(default=None, description="Safety score 0-1")
    empathy_score: Optional[float] = Field(default=None, description="Empathy score 0-1")
    clarity_score: Optional[float] = Field(default=None, description="Clarity score 0-1")
    iteration_count: int = Field(default=0, description="Number of iterations")
    total_revisions: int = Field(default=0, description="Total revision count")
