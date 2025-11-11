from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime
import uuid


class Message(BaseModel):
    """Represents a single message in the debate"""
    role: Literal["for_agent", "against_agent"]
    content: str
    timestamp: datetime = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class DebateCreate(BaseModel):
    """Request model for creating a new debate"""
    proposition: str
    for_model: str
    against_model: str


class DebateState(BaseModel):
    """Represents the state of a debate"""
    debate_id: str
    proposition: str
    for_model: str
    against_model: str
    status: Literal["created", "in_progress", "completed"] = "created"
    messages: List[Message] = []
    current_turn: int = 0
    max_turns: int = 5
    created_at: datetime = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.debate_id is None or self.debate_id == "":
            self.debate_id = str(uuid.uuid4())


class AdjudicationRequest(BaseModel):
    """Request model for adjudicating a debate"""
    adjudicator_model: str


class AdjudicationResult(BaseModel):
    """Result of debate adjudication"""
    winner: Literal["for", "against", "tie"]
    for_score: float
    against_score: float
    reasoning: str


class DebateResponse(BaseModel):
    """Response model for debate operations"""
    debate_id: str
    proposition: str
    for_model: str
    against_model: str
    status: str
    messages: List[Message]
    current_turn: int
    max_turns: int
