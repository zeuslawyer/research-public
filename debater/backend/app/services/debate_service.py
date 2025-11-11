from typing import Dict
from app.models.debate import DebateState, Message, AdjudicationResult
from app.services.llm_service import LLMService
from app.storage import debate_store
import json


class DebateService:
    """Service for managing debate logic"""

    def __init__(self):
        self.llm_service = LLMService()

    def _get_system_prompt(self, position: str, proposition: str) -> str:
        """Generate system prompt for a debate agent"""
        if position == "for":
            return f"""You are participating in a formal debate. Your role is to argue FOR the following proposition:

"{proposition}"

Provide clear, logical arguments supporting this position. Be persuasive but respectful. Keep your responses concise (2-3 paragraphs max). Address counterarguments when raised by your opponent."""
        else:
            return f"""You are participating in a formal debate. Your role is to argue AGAINST the following proposition:

"{proposition}"

Provide clear, logical arguments opposing this position. Be persuasive but respectful. Keep your responses concise (2-3 paragraphs max). Address counterarguments when raised by your opponent."""

    def _get_adjudicator_prompt(self, proposition: str, messages: list) -> str:
        """Generate prompt for adjudicator"""
        debate_transcript = "\n\n".join([
            f"{'FOR' if msg.role == 'for_agent' else 'AGAINST'}: {msg.content}"
            for msg in messages
        ])

        return f"""You are an expert debate adjudicator. You have been asked to evaluate the following debate on the proposition:

"{proposition}"

DEBATE TRANSCRIPT:
{debate_transcript}

Please evaluate this debate and provide your judgment in the following JSON format:
{{
    "winner": "for|against|tie",
    "for_score": <score from 0-100>,
    "against_score": <score from 0-100>,
    "reasoning": "<detailed explanation of your decision>"
}}

Evaluate based on:
- Strength and logic of arguments
- Use of evidence and examples
- Rebuttal effectiveness
- Clarity and persuasiveness
- Overall coherence

Respond ONLY with valid JSON, nothing else."""

    async def conduct_turn(
        self,
        debate_id: str,
        api_keys: Dict[str, str]
    ) -> DebateState:
        """
        Conduct one full turn of the debate (both agents speak)

        Args:
            debate_id: ID of the debate
            api_keys: API keys for LLM providers

        Returns:
            Updated debate state
        """
        debate = debate_store.get_debate(debate_id)
        if not debate:
            raise ValueError(f"Debate {debate_id} not found")

        if debate.status == "completed":
            raise ValueError("Debate is already completed")

        # Update status to in_progress
        if debate.status == "created":
            debate.status = "in_progress"

        # FOR agent's turn
        for_messages = self._prepare_messages_for_agent(debate.messages, "for_agent")
        for_system = self._get_system_prompt("for", debate.proposition)

        for_response = await self.llm_service.generate_response(
            model=debate.for_model,
            system_prompt=for_system,
            messages=for_messages,
            api_keys=api_keys
        )

        debate.messages.append(Message(role="for_agent", content=for_response))

        # AGAINST agent's turn
        against_messages = self._prepare_messages_for_agent(debate.messages, "against_agent")
        against_system = self._get_system_prompt("against", debate.proposition)

        against_response = await self.llm_service.generate_response(
            model=debate.against_model,
            system_prompt=against_system,
            messages=against_messages,
            api_keys=api_keys
        )

        debate.messages.append(Message(role="against_agent", content=against_response))

        # Increment turn counter
        debate.current_turn += 1

        # Check if debate is complete
        if debate.current_turn >= debate.max_turns:
            debate.status = "completed"

        # Update storage
        debate_store.update_debate(debate)

        return debate

    def _prepare_messages_for_agent(self, messages: list, agent_role: str) -> list:
        """
        Prepare conversation history for an agent

        Messages from the same agent appear as 'assistant' messages
        Messages from the opponent appear as 'user' messages
        """
        prepared = []
        for msg in messages:
            if msg.role == agent_role:
                prepared.append({"role": "assistant", "content": msg.content})
            else:
                prepared.append({"role": "user", "content": msg.content})
        return prepared

    async def adjudicate_debate(
        self,
        debate_id: str,
        adjudicator_model: str,
        api_keys: Dict[str, str]
    ) -> AdjudicationResult:
        """
        Adjudicate a completed debate

        Args:
            debate_id: ID of the debate
            adjudicator_model: Model to use for adjudication
            api_keys: API keys for LLM providers

        Returns:
            Adjudication result
        """
        debate = debate_store.get_debate(debate_id)
        if not debate:
            raise ValueError(f"Debate {debate_id} not found")

        if debate.status != "completed":
            raise ValueError("Debate must be completed before adjudication")

        # Prepare adjudication prompt
        adjudicator_prompt = self._get_adjudicator_prompt(debate.proposition, debate.messages)

        # Get adjudication
        response = await self.llm_service.generate_response(
            model=adjudicator_model,
            system_prompt="You are an expert debate adjudicator. Respond only with valid JSON.",
            messages=[{"role": "user", "content": adjudicator_prompt}],
            api_keys=api_keys
        )

        # Parse JSON response
        try:
            # Try to extract JSON from the response
            response_text = response.strip()
            if "```json" in response_text:
                # Extract from code block
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract from generic code block
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            result_dict = json.loads(response_text)
            return AdjudicationResult(**result_dict)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse adjudication response: {e}\n\nResponse: {response}")


# Global instance
debate_service = DebateService()
