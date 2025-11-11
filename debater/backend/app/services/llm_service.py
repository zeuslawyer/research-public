import anthropic
import openai
import google.generativeai as genai
from typing import List, Dict, Literal


class LLMService:
    """Service for interacting with various LLM providers"""

    # Available models
    CLAUDE_MODELS = ["claude-sonnet-4-5-20250929", "claude-3-5-sonnet-20241022"]
    GPT_MODELS = ["gpt-4o", "gpt-4-turbo"]
    GEMINI_MODELS = ["gemini-2.0-flash-exp", "gemini-1.5-pro"]

    ALL_MODELS = CLAUDE_MODELS + GPT_MODELS + GEMINI_MODELS

    def __init__(self, anthropic_key: str = None, openai_key: str = None, gemini_key: str = None):
        """Initialize LLM clients with API keys"""
        self.anthropic_key = anthropic_key
        self.openai_key = openai_key
        self.gemini_key = gemini_key

    def _get_provider(self, model: str) -> Literal["claude", "gpt", "gemini"]:
        """Determine which provider to use based on model name"""
        if model in self.CLAUDE_MODELS:
            return "claude"
        elif model in self.GPT_MODELS:
            return "gpt"
        elif model in self.GEMINI_MODELS:
            return "gemini"
        else:
            raise ValueError(f"Unknown model: {model}")

    async def generate_response(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        api_keys: Dict[str, str]
    ) -> str:
        """
        Generate a response from the specified model

        Args:
            model: Model identifier
            system_prompt: System prompt for the model
            messages: List of conversation messages
            api_keys: Dictionary containing API keys for all providers

        Returns:
            Generated response text
        """
        provider = self._get_provider(model)

        if provider == "claude":
            return await self._call_claude(model, system_prompt, messages, api_keys.get("anthropic"))
        elif provider == "gpt":
            return await self._call_gpt(model, system_prompt, messages, api_keys.get("openai"))
        elif provider == "gemini":
            return await self._call_gemini(model, system_prompt, messages, api_keys.get("gemini"))

    async def _call_claude(self, model: str, system_prompt: str, messages: List[Dict[str, str]], api_key: str) -> str:
        """Call Claude API"""
        if not api_key:
            raise ValueError("Anthropic API key not provided")

        client = anthropic.Anthropic(api_key=api_key)

        # Convert messages to Claude format
        claude_messages = [
            {"role": "user" if msg["role"] in ["user", "against_agent", "for_agent"] else "assistant",
             "content": msg["content"]}
            for msg in messages
        ]

        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_prompt,
            messages=claude_messages
        )

        return response.content[0].text

    async def _call_gpt(self, model: str, system_prompt: str, messages: List[Dict[str, str]], api_key: str) -> str:
        """Call OpenAI GPT API"""
        if not api_key:
            raise ValueError("OpenAI API key not provided")

        client = openai.AsyncOpenAI(api_key=api_key)

        # Convert messages to GPT format
        gpt_messages = [{"role": "system", "content": system_prompt}]
        gpt_messages.extend([
            {"role": "user" if msg["role"] in ["user", "against_agent", "for_agent"] else "assistant",
             "content": msg["content"]}
            for msg in messages
        ])

        response = await client.chat.completions.create(
            model=model,
            messages=gpt_messages,
            max_tokens=2048
        )

        return response.choices[0].message.content

    async def _call_gemini(self, model: str, system_prompt: str, messages: List[Dict[str, str]], api_key: str) -> str:
        """Call Google Gemini API"""
        if not api_key:
            raise ValueError("Gemini API key not provided")

        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt
        )

        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "against_agent", "for_agent"] else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})

        chat = gemini_model.start_chat(history=gemini_messages[:-1] if gemini_messages else [])
        response = chat.send_message(gemini_messages[-1]["parts"][0] if gemini_messages else "")

        return response.text

    @classmethod
    def get_available_models(cls) -> Dict[str, List[str]]:
        """Get all available models grouped by provider"""
        return {
            "claude": cls.CLAUDE_MODELS,
            "gpt": cls.GPT_MODELS,
            "gemini": cls.GEMINI_MODELS
        }
