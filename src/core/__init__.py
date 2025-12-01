"""Core package initialization."""

from .entities import Issue, CodeChange, ChangeType, PullRequest, ReviewResult
from .value_objects import Severity, ReviewStatus
from .interfaces import LLMProvider, GitHubClient, CodeAnalyzer

__all__ = [
    # Entities
    "Issue",
    "CodeChange",
    "ChangeType",
    "PullRequest",
    "ReviewResult",
    # Value Objects
    "Severity",
    "ReviewStatus",
    # Interfaces
    "LLMProvider",
    "GitHubClient",
    "CodeAnalyzer",
]
