"""Abstract interface for LLM providers."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class LLMProvider(ABC):
    """Abstract base class for LLM providers following Strategy Pattern."""
    
    def __init__(self, api_key: str, model_name: str, **kwargs):
        """
        Initialize LLM provider.
        
        Args:
            api_key: API key for authentication
            model_name: Name of the model to use
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text based on prompt.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
            
        Raises:
            LLMProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    async def generate_async(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Asynchronously generate text based on prompt.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
            
        Raises:
            LLMProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_format: Dict[str, Any],
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON) based on prompt.
        
        Args:
            prompt: Input prompt
            response_format: Expected response structure
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Structured response as dictionary
            
        Raises:
            LLMProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the provider is properly configured and can connect.
        
        Returns:
            True if connection is valid
            
        Raises:
            LLMProviderError: If validation fails
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the LLM provider."""
        pass
    
    @property
    @abstractmethod
    def max_context_length(self) -> int:
        """Return maximum context length for the model."""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "max_context_length": self.max_context_length,
        }
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.provider_name} ({self.model_name})"
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"{self.__class__.__name__}(model='{self.model_name}')"
