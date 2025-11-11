from .debate import router as debate_router
from .rag import router as rag_router
from .mcp import router as mcp_router

__all__ = ["debate_router", "rag_router", "mcp_router"]
