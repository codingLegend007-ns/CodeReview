"""GitHub API client implementation."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import base64

from github import Github, GithubException
from github.PullRequest import PullRequest as GithubPR
from github.Repository import Repository

from ...core.interfaces.github_client import GitHubClient as GitHubClientInterface
from ...core.entities import PullRequest, CodeChange, ChangeType
from ..exceptions import GitHubClientError, RateLimitError, AuthenticationError


class GitHubClient(GitHubClientInterface):
    """GitHub API client using PyGithub."""
    
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        """Initialize GitHub client."""
        super().__init__(token, base_url)
        try:
            self._client = Github(token, base_url=base_url)
            self._test_connection()
        except GithubException as e:
            if e.status == 401:
                raise AuthenticationError("Invalid GitHub token")
            raise GitHubClientError(f"Failed to initialize GitHub client: {e}")
    
    def _test_connection(self):
        """Test GitHub connection."""
        try:
            self._client.get_user().login
        except GithubException as e:
            if e.status == 401:
                raise AuthenticationError("Invalid GitHub token")
            raise GitHubClientError(f"Connection test failed: {e}")
    
    def _get_repository(self, repository: str) -> Repository:
        """Get repository object."""
        try:
            return self._client.get_repo(repository)
        except GithubException as e:
            if e.status == 404:
                raise GitHubClientError(f"Repository '{repository}' not found")
            elif e.status == 403:
                raise RateLimitError("GitHub API rate limit exceeded")
            raise GitHubClientError(f"Failed to get repository: {e}")
    
    def get_pull_request(
        self,
        repository: str,
        pr_number: int,
        include_files: bool = True
    ) -> PullRequest:
        """Fetch a pull request by number."""
        try:
            repo = self._get_repository(repository)
            pr = repo.get_pull(pr_number)
            
            # Convert to domain entity
            pull_request = self._convert_pr(pr, repository)
            
            if include_files:
                pull_request.changes = self.get_pull_request_files(repository, pr_number)
            
            return pull_request
            
        except GithubException as e:
            if e.status == 404:
                raise GitHubClientError(f"Pull request #{pr_number} not found")
            elif e.status == 403:
                raise RateLimitError("GitHub API rate limit exceeded")
            raise GitHubClientError(f"Failed to fetch PR: {e}")
    
    def get_pull_request_files(
        self,
        repository: str,
        pr_number: int
    ) -> List[CodeChange]:
        """Fetch files changed in a pull request."""
        try:
            repo = self._get_repository(repository)
            pr = repo.get_pull(pr_number)
            
            changes = []
            for file in pr.get_files():
                change = self._convert_file(file)
                changes.append(change)
            
            return changes
            
        except GithubException as e:
            if e.status == 403:
                raise RateLimitError("GitHub API rate limit exceeded")
            raise GitHubClientError(f"Failed to fetch PR files: {e}")
    
    def get_file_content(
        self,
        repository: str,
        file_path: str,
        ref: str
    ) -> str:
        """Fetch content of a specific file."""
        try:
            repo = self._get_repository(repository)
            content_file = repo.get_contents(file_path, ref=ref)
            
            if content_file.encoding == "base64":
                return base64.b64decode(content_file.content).decode("utf-8")
            return content_file.decoded_content.decode("utf-8")
            
        except GithubException as e:
            if e.status == 404:
                raise GitHubClientError(f"File '{file_path}' not found at ref '{ref}'")
            raise GitHubClientError(f"Failed to fetch file content: {e}")
        except Exception as e:
            raise GitHubClientError(f"Failed to decode file content: {e}")
    
    def get_pull_request_diff(
        self,
        repository: str,
        pr_number: int
    ) -> str:
        """Fetch the unified diff for a pull request."""
        try:
            repo = self._get_repository(repository)
            pr = repo.get_pull(pr_number)
            
            # Get diff from files
            files = pr.get_files()
            diff_parts = []
            
            for file in files:
                if file.patch:
                    diff_parts.append(f"--- a/{file.filename}\n+++ b/{file.filename}\n{file.patch}")
            
            return "\n\n".join(diff_parts)
            
        except GithubException as e:
            raise GitHubClientError(f"Failed to fetch PR diff: {e}")
    
    def list_pull_requests(
        self,
        repository: str,
        state: str = "open",
        limit: int = 30
    ) -> List[PullRequest]:
        """List pull requests in a repository."""
        try:
            repo = self._get_repository(repository)
            prs = repo.get_pulls(state=state)
            
            result = []
            for i, pr in enumerate(prs):
                if i >= limit:
                    break
                result.append(self._convert_pr(pr, repository))
            
            return result
            
        except GithubException as e:
            raise GitHubClientError(f"Failed to list PRs: {e}")
    
    def post_comment(
        self,
        repository: str,
        pr_number: int,
        comment: str
    ) -> bool:
        """Post a comment on a pull request."""
        try:
            repo = self._get_repository(repository)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            return True
            
        except GithubException as e:
            raise GitHubClientError(f"Failed to post comment: {e}")
    
    def validate_connection(self) -> bool:
        """Validate GitHub connection."""
        try:
            self._client.get_user().login
            return True
        except GithubException:
            return False
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """Get current API rate limit status."""
        try:
            overview = self._client.get_rate_limit()

            resources: Dict[str, Any] = {}
            primary_resources = ("core", "search", "graphql", "integration_manifest", "source_import", "code_search")

            for name in primary_resources:
                resource = self._extract_rate_resource(overview, name)
                if resource is not None:
                    resources[name] = self._serialize_rate_resource(resource)

            extra_resources = getattr(overview, "resources", None)
            if isinstance(extra_resources, dict):
                for name, resource in extra_resources.items():
                    if name not in resources:
                        resources[name] = self._serialize_rate_resource(resource)

            if "core" not in resources:
                resources["core"] = self._serialize_rate_resource(None)
            if "search" not in resources:
                resources["search"] = self._serialize_rate_resource(None)

            return resources
        except GithubException as e:
            raise GitHubClientError(f"Failed to get rate limit: {e}")

    def _extract_rate_resource(self, overview: Any, name: str) -> Any:
        """Safely extract a rate limit resource from the overview."""
        resource = getattr(overview, name, None)
        if resource is None:
            resources = getattr(overview, "resources", None)
            if isinstance(resources, dict):
                resource = resources.get(name)
        return resource

    def _serialize_rate_resource(self, resource: Any) -> Dict[str, Any]:
        """Normalize rate limit resource to a serializable dictionary."""
        if resource is None:
            return {"limit": None, "remaining": None, "reset": None}

        if isinstance(resource, dict):
            limit = resource.get("limit")
            remaining = resource.get("remaining")
            reset = resource.get("reset")
        else:
            limit = getattr(resource, "limit", None)
            remaining = getattr(resource, "remaining", None)
            reset = getattr(resource, "reset", None)

        return {
            "limit": limit,
            "remaining": remaining,
            "reset": self._format_reset_value(reset),
        }

    @staticmethod
    def _format_reset_value(value: Any) -> Any:
        """Format reset value for readability."""
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    
    def _convert_pr(self, pr: GithubPR, repository: str) -> PullRequest:
        """Convert PyGithub PR to domain entity."""
        return PullRequest(
            number=pr.number,
            title=pr.title,
            description=pr.body,
            author=pr.user.login,
            repository=repository,
            base_branch=pr.base.ref,
            head_branch=pr.head.ref,
            state=pr.state,
            created_at=pr.created_at,
            updated_at=pr.updated_at,
            url=pr.html_url,
            total_additions=pr.additions,
            total_deletions=pr.deletions,
            total_changes=pr.additions + pr.deletions,
            changed_files_count=pr.changed_files,
        )
    
    def _convert_file(self, file) -> CodeChange:
        """Convert PyGithub file to domain entity."""
        # Determine change type
        if file.status == "added":
            status = ChangeType.ADDED
        elif file.status == "removed":
            status = ChangeType.DELETED
        elif file.status == "renamed":
            status = ChangeType.RENAMED
        else:
            status = ChangeType.MODIFIED
        
        # Detect language from file extension
        language = self._detect_language(file.filename)
        
        return CodeChange(
            filename=file.filename,
            status=status,
            additions=file.additions,
            deletions=file.deletions,
            changes=file.changes,
            patch=file.patch,
            previous_filename=file.previous_filename,
            language=language,
            is_binary=file.patch is None and file.changes > 0,
        )
    
    def _detect_language(self, filename: str) -> Optional[str]:
        """Detect programming language from filename."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".r": "r",
            ".sql": "sql",
            ".sh": "shell",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".md": "markdown",
        }
        
        for ext, lang in language_map.items():
            if filename.endswith(ext):
                return lang
        
        return None
