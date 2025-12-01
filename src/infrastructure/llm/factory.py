"""LLM provider factory."""

from typing import Optional
from ...core.interfaces.llm_provider import LLMProvider
from .gemini_provider import GeminiProvider
from .grok_provider import GrokProvider
from ..exceptions import ConfigurationError


class LLMProviderFactory:
    """Factory for creating LLM provider instances following Factory Pattern."""
    
    _providers = {
        "gemini": GeminiProvider,
        "grok": GrokProvider,
    }
    
    @classmethod
    def create(
        cls,
        provider_name: str,
        api_key: str,
        model_name: Optional[str] = None,
        **kwargs
    ) -> LLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_name: Name of the provider (gemini, grok)
            api_key: API key for authentication
            model_name: Model name (optional, uses defaults)
            **kwargs: Additional provider-specific arguments
            
        Returns:
            LLMProvider instance
            
        Raises:
            ConfigurationError: If provider is unknown or creation fails
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ConfigurationError(
                f"Unknown LLM provider: {provider_name}. "
                f"Available providers: {available}"
            )
        
        provider_class = cls._providers[provider_name]
        
        try:
            if model_name:
                return provider_class(api_key, model_name, **kwargs)
            else:
                return provider_class(api_key, **kwargs)
        except Exception as e:
            raise ConfigurationError(f"Failed to create {provider_name} provider: {e}")
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        Register a custom LLM provider.
        
        Args:
            name: Provider name
            provider_class: Provider class implementing LLMProvider interface
        """
        if not issubclass(provider_class, LLMProvider):
            raise ValueError(f"{provider_class} must inherit from LLMProvider")
        
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def list_providers(cls) -> list:
        """List available provider names."""
        return list(cls._providers.keys())
