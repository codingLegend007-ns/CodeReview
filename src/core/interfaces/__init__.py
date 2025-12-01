"""Core interfaces package."""

from .llm_provider import LLMProvider
from .github_client import GitHubClient
from .code_analyzer import CodeAnalyzer

__all__ = [
    "LLMProvider",
    "GitHubClient",
    "CodeAnalyzer",
]
