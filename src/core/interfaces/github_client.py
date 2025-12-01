"""Abstract interface for GitHub clients."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.pull_request import PullRequest
from ..entities.code_change import CodeChange


class GitHubClient(ABC):
    """Abstract base class for GitHub API clients following Repository Pattern."""
    
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token
            base_url: Base URL for GitHub API
        """
        self.token = token
        self.base_url = base_url
    
    @abstractmethod
    def get_pull_request(
        self,
        repository: str,
        pr_number: int,
        include_files: bool = True
    ) -> PullRequest:
        """
        Fetch a pull request by number.
        
        Args:
            repository: Repository in format "owner/repo"
            pr_number: Pull request number
            include_files: Whether to fetch file changes
            
        Returns:
            PullRequest entity
            
        Raises:
            GitHubClientError: If request fails
        """
        pass
    
    @abstractmethod
    def get_pull_request_files(
        self,
        repository: str,
        pr_number: int
    ) -> List[CodeChange]:
        """
        Fetch files changed in a pull request.
        
        Args:
            repository: Repository in format "owner/repo"
            pr_number: Pull request number
            
        Returns:
            List of CodeChange entities
            
        Raises:
            GitHubClientError: If request fails
        """
        pass
    
    @abstractmethod
    def get_file_content(
        self,
        repository: str,
        file_path: str,
        ref: str
    ) -> str:
        """
        Fetch content of a specific file at a given reference.
        
        Args:
            repository: Repository in format "owner/repo"
            file_path: Path to the file
            ref: Git reference (branch, commit, tag)
            
        Returns:
            File content as string
            
        Raises:
            GitHubClientError: If request fails
        """
        pass
    
    @abstractmethod
    def get_pull_request_diff(
        self,
        repository: str,
        pr_number: int
    ) -> str:
        """
        Fetch the unified diff for a pull request.
        
        Args:
            repository: Repository in format "owner/repo"
            pr_number: Pull request number
            
        Returns:
            Unified diff as string
            
        Raises:
            GitHubClientError: If request fails
        """
        pass
    
    @abstractmethod
    def list_pull_requests(
        self,
        repository: str,
        state: str = "open",
        limit: int = 30
    ) -> List[PullRequest]:
        """
        List pull requests in a repository.
        
        Args:
            repository: Repository in format "owner/repo"
            state: PR state filter (open, closed, all)
            limit: Maximum number of PRs to return
            
        Returns:
            List of PullRequest entities
            
        Raises:
            GitHubClientError: If request fails
        """
        pass
    
    @abstractmethod
    def post_comment(
        self,
        repository: str,
        pr_number: int,
        comment: str
    ) -> bool:
        """
        Post a comment on a pull request.
        
        Args:
            repository: Repository in format "owner/repo"
            pr_number: Pull request number
            comment: Comment text
            
        Returns:
            True if comment was posted successfully
            
        Raises:
            GitHubClientError: If request fails
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the client can connect to GitHub.
        
        Returns:
            True if connection is valid
            
        Raises:
            GitHubClientError: If validation fails
        """
        pass
    
    @abstractmethod
    def get_rate_limit(self) -> Dict[str, Any]:
        """
        Get current API rate limit status.
        
        Returns:
            Dictionary with rate limit information
            
        Raises:
            GitHubClientError: If request fails
        """
        pass
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"GitHubClient(base_url={self.base_url})"
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"{self.__class__.__name__}(base_url='{self.base_url}')"
