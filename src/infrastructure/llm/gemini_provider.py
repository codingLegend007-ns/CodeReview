"""Google Gemini LLM provider implementation."""

from typing import Optional, Dict, Any
import json
import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.generativeai.types import GenerationConfig

from ...core.interfaces.llm_provider import LLMProvider
from ..exceptions import LLMProviderError


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider implementation."""
    
    # Model context lengths
    MODEL_CONTEXT_LENGTHS = {
        "gemini-pro": 32768,
        "gemini-1.5-pro-latest": 1048576,  # 1M tokens
        "gemini-1.5-flash-latest": 1048576,
        "gemini-1.5-flash": 1048576,
        "gemini-1.5-pro": 1048576,
    }

    MODEL_ALIASES = {
        "gemini-1.5-flash": "gemini-1.5-flash-latest",
        "gemini-1.5-pro": "gemini-1.5-pro-latest",
        "1.5-flash": "gemini-1.5-flash-latest",
        "1.5-pro": "gemini-1.5-pro-latest",
        "flash": "gemini-1.5-flash-latest",
        "pro": "gemini-1.5-pro-latest",
    }

    DEFAULT_MODEL = "gemini-1.5-pro-latest"
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro-latest", **kwargs):
        """Initialize Gemini provider."""
        normalized_model = self._normalize_model_name(model_name)
        super().__init__(api_key, normalized_model, **kwargs)
        self.original_model_name = model_name
        
        try:
            genai.configure(api_key=api_key)
            self._model = GenerativeModel(self.model_name)
            self._validate()
        except Exception as e:
            raise LLMProviderError(f"Failed to initialize Gemini provider: {e}")

    @classmethod
    def _normalize_model_name(cls, model_name: Optional[str]) -> str:
        """Normalize model name to supported identifier."""
        if not model_name:
            return cls.DEFAULT_MODEL
        candidate = model_name.strip()
        alias = cls.MODEL_ALIASES.get(candidate.lower())
        if alias:
            return alias
        if candidate.startswith("gemini-1.5-") and not candidate.endswith("-latest"):
            return f"{candidate}-latest"
        return candidate
    
    def _validate(self):
        """Validate model configuration."""
        try:
            # Test with a simple prompt
            self._model.generate_content("Hello")
        except Exception as e:
            raise LLMProviderError(f"Gemini validation failed: {e}")
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text using Gemini."""
        try:
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )
            
            response = self._model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if not response.text:
                raise LLMProviderError("Empty response from Gemini")
            
            return response.text
            
        except Exception as e:
            raise LLMProviderError(f"Gemini generation failed: {e}")
    
    async def generate_async(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Asynchronously generate text using Gemini."""
        try:
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )
            
            response = await self._model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            if not response.text:
                raise LLMProviderError("Empty response from Gemini")
            
            return response.text
            
        except Exception as e:
            raise LLMProviderError(f"Gemini async generation failed: {e}")
    
    def generate_structured(
        self,
        prompt: str,
        response_format: Dict[str, Any],
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON output using Gemini."""
        try:
            # Add JSON formatting instruction to prompt
            structured_prompt = (
                f"{prompt}\n\n"
                f"Respond ONLY with valid JSON in the following format:\n"
                f"{json.dumps(response_format, indent=2)}\n\n"
                f"Do not include any text before or after the JSON object."
            )
            
            response_text = self.generate(
                structured_prompt,
                temperature=temperature,
                **kwargs
            )
            
            # Extract JSON from response
            response_text = response_text.strip()
            
            # Handle markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                raise LLMProviderError(f"Failed to parse JSON response: {e}\nResponse: {response_text}")
            
        except Exception as e:
            raise LLMProviderError(f"Gemini structured generation failed: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        try:
            result = self._model.count_tokens(text)
            return result.total_tokens
        except Exception as e:
            # Fallback: rough estimation (4 chars per token)
            return len(text) // 4
    
    def validate_connection(self) -> bool:
        """Validate Gemini connection."""
        try:
            self._model.generate_content("Test")
            return True
        except Exception:
            return False
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "google-gemini"
    
    @property
    def max_context_length(self) -> int:
        """Return maximum context length."""
        return self.MODEL_CONTEXT_LENGTHS.get(self.model_name, 32768)
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"Google Gemini ({self.model_name})"
