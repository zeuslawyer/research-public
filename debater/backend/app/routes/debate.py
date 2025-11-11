from fastapi import APIRouter, HTTPException, Body
from typing import Dict
from app.models.debate import (
    DebateCreate,
    DebateState,
    DebateResponse,
    AdjudicationRequest,
    AdjudicationResult
)
from app.storage import debate_store
from app.services import debate_service
import uuid

router = APIRouter(prefix="/debate", tags=["debate"])


@router.post("/create", response_model=DebateResponse)
async def create_debate(debate_data: DebateCreate):
    """
    Create a new debate with a proposition and model selections

    Args:
        debate_data: Debate configuration including proposition and models

    Returns:
        Created debate state
    """
    debate = DebateState(
        debate_id=str(uuid.uuid4()),
        proposition=debate_data.proposition,
        for_model=debate_data.for_model,
        against_model=debate_data.against_model,
        status="created"
    )

    debate_store.create_debate(debate)

    return DebateResponse(
        debate_id=debate.debate_id,
        proposition=debate.proposition,
        for_model=debate.for_model,
        against_model=debate.against_model,
        status=debate.status,
        messages=debate.messages,
        current_turn=debate.current_turn,
        max_turns=debate.max_turns
    )


@router.get("/{debate_id}", response_model=DebateResponse)
async def get_debate(debate_id: str):
    """
    Get the current state of a debate

    Args:
        debate_id: Unique debate identifier

    Returns:
        Current debate state
    """
    debate = debate_store.get_debate(debate_id)
    if not debate:
        raise HTTPException(status_code=404, detail=f"Debate {debate_id} not found")

    return DebateResponse(
        debate_id=debate.debate_id,
        proposition=debate.proposition,
        for_model=debate.for_model,
        against_model=debate.against_model,
        status=debate.status,
        messages=debate.messages,
        current_turn=debate.current_turn,
        max_turns=debate.max_turns
    )


@router.post("/{debate_id}/start")
async def start_debate(
    debate_id: str,
    api_keys: Dict[str, str] = Body(...)
):
    """
    Start the debate (conduct all turns until completion)

    Args:
        debate_id: Unique debate identifier
        api_keys: API keys for LLM providers (anthropic, openai, gemini)

    Returns:
        Updated debate state after all turns
    """
    debate = debate_store.get_debate(debate_id)
    if not debate:
        raise HTTPException(status_code=404, detail=f"Debate {debate_id} not found")

    if debate.status not in ["created", "in_progress"]:
        raise HTTPException(status_code=400, detail="Debate is already completed")

    try:
        # Conduct all turns until completion
        while debate.status != "completed":
            debate = await debate_service.conduct_turn(debate_id, api_keys)

        return DebateResponse(
            debate_id=debate.debate_id,
            proposition=debate.proposition,
            for_model=debate.for_model,
            against_model=debate.against_model,
            status=debate.status,
            messages=debate.messages,
            current_turn=debate.current_turn,
            max_turns=debate.max_turns
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during debate: {str(e)}")


@router.post("/{debate_id}/adjudicate", response_model=AdjudicationResult)
async def adjudicate_debate(
    debate_id: str,
    request: AdjudicationRequest,
    api_keys: Dict[str, str] = Body(...)
):
    """
    Adjudicate a completed debate

    Args:
        debate_id: Unique debate identifier
        request: Adjudication request with model selection
        api_keys: API keys for LLM providers

    Returns:
        Adjudication result with scores and reasoning
    """
    debate = debate_store.get_debate(debate_id)
    if not debate:
        raise HTTPException(status_code=404, detail=f"Debate {debate_id} not found")

    if debate.status != "completed":
        raise HTTPException(status_code=400, detail="Debate must be completed before adjudication")

    try:
        result = await debate_service.adjudicate_debate(
            debate_id,
            request.adjudicator_model,
            api_keys
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during adjudication: {str(e)}")


@router.get("/")
async def list_debates():
    """
    List all debates in the system

    Returns:
        List of all debates
    """
    debates = debate_store.list_debates()
    return [
        DebateResponse(
            debate_id=d.debate_id,
            proposition=d.proposition,
            for_model=d.for_model,
            against_model=d.against_model,
            status=d.status,
            messages=d.messages,
            current_turn=d.current_turn,
            max_turns=d.max_turns
        )
        for d in debates
    ]


@router.get("/models/available")
async def get_available_models():
    """
    Get all available LLM models grouped by provider

    Returns:
        Dictionary of available models by provider
    """
    from app.services.llm_service import LLMService
    return LLMService.get_available_models()
