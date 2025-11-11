from fastapi import APIRouter

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/")
async def mcp_root():
    """
    MCP (Model Context Protocol) route placeholder

    This endpoint is a scaffold for future MCP operations.
    """
    return {
        "message": "MCP endpoint - scaffold for future implementation",
        "status": "not_implemented"
    }


@router.get("/health")
async def mcp_health():
    """Health check for MCP service"""
    return {"status": "ok", "service": "mcp"}
