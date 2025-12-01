"""Custom exceptions for the application."""


class CodeReviewError(Exception):
    """Base exception for code review errors."""
    pass


class GitHubClientError(CodeReviewError):
    """Exception for GitHub client errors."""
    pass


class LLMProviderError(CodeReviewError):
    """Exception for LLM provider errors."""
    pass


class AnalyzerError(CodeReviewError):
    """Exception for code analyzer errors."""
    pass


class ConfigurationError(CodeReviewError):
    """Exception for configuration errors."""
    pass


class ValidationError(CodeReviewError):
    """Exception for validation errors."""
    pass


class RateLimitError(CodeReviewError):
    """Exception for API rate limit errors."""
    pass


class AuthenticationError(CodeReviewError):
    """Exception for authentication errors."""
    pass
