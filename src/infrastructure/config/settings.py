"""Configuration management using Pydantic."""

from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # GitHub Configuration
    github_token: str = Field(..., description="GitHub personal access token")
    github_api_url: str = Field(
        default="https://api.github.com",
        description="GitHub API base URL",
        username = "hello.harta",
        password="hello@123"
    )
    
    # Google Gemini Configuration
    google_api_key: str = Field(..., description="Google Gemini API key")
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        description="Google Gemini model name"
    )
    
    # Grok Configuration (Optional)
    grok_api_key: Optional[str] = Field(default=None, description="Grok API key")
    grok_api_url: str = Field(
        default="https://api.x.ai/v1",
        description="Grok API base URL"
    )
    grok_model: str = Field(default="grok-beta", description="Grok model name")
    
    # Default LLM Provider
    default_llm_provider: str = Field(
        default="gemini",
        description="Default LLM provider (gemini or grok)"
    )
    
    # Application Settings
    log_level: str = Field(default="INFO", description="Logging level")
    max_files_per_review: int = Field(
        default=50,
        description="Maximum files to review per PR"
    )
    max_file_size_kb: int = Field(
        default=500,
        description="Maximum file size in KB to review"
    )
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl_hours: int = Field(default=24, description="Cache TTL in hours")
    
    # Review Configuration
    parallel_processing: bool = Field(
        default=True,
        description="Enable parallel file processing"
    )
    max_workers: int = Field(default=4, description="Maximum parallel workers")
    timeout_seconds: int = Field(default=300, description="Operation timeout")
    
    # Output Settings
    output_format: str = Field(
        default="markdown",
        description="Output format (markdown, json, html)"
    )
    verbose: bool = Field(default=False, description="Verbose output")
    color_output: bool = Field(default=True, description="Colorized output")
    
    # Rate Limiting
    github_rate_limit_pause: int = Field(
        default=60,
        description="Seconds to pause on GitHub rate limit"
    )
    llm_rate_limit_pause: int = Field(
        default=10,
        description="Seconds to pause on LLM rate limit"
    )
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    # Security
    validate_ssl: bool = Field(default=True, description="Validate SSL certificates")
    mask_sensitive_data: bool = Field(
        default=True,
        description="Mask sensitive data in logs"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v
    
    @field_validator("default_llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate LLM provider."""
        v = v.lower()
        if v not in ["gemini", "grok"]:
            raise ValueError("Invalid LLM provider. Must be 'gemini' or 'grok'")
        return v
    
    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """Validate output format."""
        v = v.lower()
        if v not in ["markdown", "json", "html"]:
            raise ValueError("Invalid output format. Must be 'markdown', 'json', or 'html'")
        return v
    
    @field_validator("max_workers")
    @classmethod
    def validate_max_workers(cls, v: int) -> int:
        """Validate max workers."""
        if v < 1 or v > 10:
            raise ValueError("max_workers must be between 1 and 10")
        return v
    
    def get_llm_config(self, provider: Optional[str] = None) -> dict:
        """Get LLM configuration for specified provider."""
        provider = provider or self.default_llm_provider
        
        if provider == "gemini":
            from ..llm.gemini_provider import GeminiProvider  # local import to avoid circular

            normalized_model = GeminiProvider._normalize_model_name(self.gemini_model)
            if normalized_model != self.gemini_model:
                # Persist normalized value for subsequent access
                object.__setattr__(self, "gemini_model", normalized_model)
            return {
                "provider": "gemini",
                "api_key": self.google_api_key,
                "model": normalized_model,
            }
        elif provider == "grok":
            if not self.grok_api_key:
                raise ValueError("Grok API key not configured")
            return {
                "provider": "grok",
                "api_key": self.grok_api_key,
                "api_url": self.grok_api_url,
                "model": self.grok_model,
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def __repr__(self) -> str:
        """Return safe representation without sensitive data."""
        return (
            f"Settings("
            f"github_api_url={self.github_api_url}, "
            f"default_llm_provider={self.default_llm_provider}, "
            f"log_level={self.log_level})"
        )


# Singleton instance
_settings: Optional[Settings] = None


def get_settings(force_reload: bool = False) -> Settings:
    """
    Get application settings singleton.
    
    Args:
        force_reload: Force reload settings from environment
        
    Returns:
        Settings instance
    """
    global _settings
    
    if _settings is None or force_reload:
        _settings = Settings()
    
    return _settings
