from fastapi import APIRouter

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/")
async def rag_root():
    """
    RAG route placeholder

    This endpoint is a scaffold for future RAG (Retrieval-Augmented Generation) operations.
    """
    return {
        "message": "RAG endpoint - scaffold for future implementation",
        "status": "not_implemented"
    }


@router.get("/health")
async def rag_health():
    """Health check for RAG service"""
    return {"status": "ok", "service": "rag"}
