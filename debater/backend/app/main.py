from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import debate_router, rag_router, mcp_router

# Create FastAPI app
app = FastAPI(
    title="Debate System API",
    description="Backend API for AI-powered debate system with RAG and MCP support",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(debate_router)
app.include_router(rag_router)
app.include_router(mcp_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Debate System API",
        "version": "1.0.0",
        "endpoints": {
            "debate": "/debate",
            "rag": "/rag",
            "mcp": "/mcp",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
