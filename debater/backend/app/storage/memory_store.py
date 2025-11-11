from typing import Dict, Optional
from app.models.debate import DebateState


class DebateStore:
    """In-memory storage for debates"""

    def __init__(self):
        self._debates: Dict[str, DebateState] = {}

    def create_debate(self, debate: DebateState) -> DebateState:
        """Store a new debate"""
        self._debates[debate.debate_id] = debate
        return debate

    def get_debate(self, debate_id: str) -> Optional[DebateState]:
        """Retrieve a debate by ID"""
        return self._debates.get(debate_id)

    def update_debate(self, debate: DebateState) -> DebateState:
        """Update an existing debate"""
        self._debates[debate.debate_id] = debate
        return debate

    def list_debates(self) -> list[DebateState]:
        """List all debates"""
        return list(self._debates.values())

    def delete_debate(self, debate_id: str) -> bool:
        """Delete a debate"""
        if debate_id in self._debates:
            del self._debates[debate_id]
            return True
        return False


# Global instance
debate_store = DebateStore()
