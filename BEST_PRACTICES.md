# Development Best Practices Guide

## Overview

This guide ensures you build a professional, maintainable, and scalable AI code review system following industry best practices.

## 🏗️ Architecture Principles

### SOLID Principles in Practice

#### 1. Single Responsibility Principle (SRP)
**Rule**: Each class should have one, and only one, reason to change.

**Examples in this project**:
- ✅ `GitHubClient` - Only handles GitHub API interactions
- ✅ `GeminiProvider` - Only manages Gemini LLM interactions
- ✅ `CodeReviewerAgent` - Only performs code quality analysis
- ❌ Avoid: A class that fetches data, processes it, and displays it

**How to apply**:
```python
# Good
class GitHubClient:
    def get_pull_request(self, repo, pr_number):
        # Only fetches PR data
        pass

class PRAnalyzer:
    def analyze(self, pull_request):
        # Only analyzes PR
        pass

# Bad
class GitHubManager:
    def get_pull_request(self, repo, pr_number):
        pr = self._fetch_pr()
        analysis = self._analyze_pr(pr)
        self._save_to_database(analysis)
        return self._format_output(analysis)
```

#### 2. Open/Closed Principle (OCP)
**Rule**: Software entities should be open for extension but closed for modification.

**Examples in this project**:
```python
# Base interface - closed for modification
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

# Extended for new providers - open for extension
class GeminiProvider(LLMProvider):
    def generate(self, prompt: str) -> str:
        # Gemini-specific implementation
        pass

class ClaudeProvider(LLMProvider):  # New provider without modifying base
    def generate(self, prompt: str) -> str:
        # Claude-specific implementation
        pass
```

#### 3. Liskov Substitution Principle (LSP)
**Rule**: Derived classes must be substitutable for their base classes.

**Examples**:
```python
# Any LLM provider can be used interchangeably
def review_code(llm: LLMProvider, code: str) -> str:
    return llm.generate(f"Review this code: {code}")

# All of these work without changes to review_code
gemini = GeminiProvider(api_key)
grok = GrokProvider(api_key)

review_code(gemini, code)  # Works
review_code(grok, code)    # Works
```

#### 4. Interface Segregation Principle (ISP)
**Rule**: Clients should not be forced to depend on interfaces they don't use.

**Examples**:
```python
# Bad - fat interface
class CodeReviewSystem(ABC):
    @abstractmethod
    def review_code(self): pass
    @abstractmethod
    def scan_security(self): pass
    @abstractmethod
    def check_performance(self): pass
    @abstractmethod
    def generate_report(self): pass

# Good - segregated interfaces
class CodeAnalyzer(ABC):
    @abstractmethod
    def analyze(self): pass

class SecurityScanner(ABC):
    @abstractmethod
    def scan(self): pass

class ReportGenerator(ABC):
    @abstractmethod
    def generate(self): pass
```

#### 5. Dependency Inversion Principle (DIP)
**Rule**: Depend on abstractions, not concretions.

**Examples**:
```python
# Good - depends on abstraction
class ReviewOrchestrator:
    def __init__(self, github: GitHubClient, llm: LLMProvider):
        self.github = github
        self.llm = llm

# Can inject any implementation
orchestrator = ReviewOrchestrator(
    github=GitHubClient(token),
    llm=GeminiProvider(api_key)
)

# Or swap implementations
orchestrator = ReviewOrchestrator(
    github=MockGitHubClient(),
    llm=GrokProvider(api_key)
)
```

## 🎨 Design Patterns

### 1. Strategy Pattern
**Use case**: Switching between different LLM providers

```python
# Context
class CodeReviewer:
    def __init__(self, llm_strategy: LLMProvider):
        self._llm = llm_strategy
    
    def review(self, code: str) -> str:
        return self._llm.generate(f"Review: {code}")

# Strategies
gemini = GeminiProvider(api_key)
grok = GrokProvider(api_key)

# Switch strategies at runtime
reviewer = CodeReviewer(gemini)
reviewer = CodeReviewer(grok)
```

### 2. Factory Pattern
**Use case**: Creating LLM providers

```python
# Factory
class LLMProviderFactory:
    @classmethod
    def create(cls, provider_name: str, **config) -> LLMProvider:
        if provider_name == "gemini":
            return GeminiProvider(**config)
        elif provider_name == "grok":
            return GrokProvider(**config)
        raise ValueError(f"Unknown provider: {provider_name}")

# Usage
llm = LLMProviderFactory.create("gemini", api_key=key)
```

### 3. Repository Pattern
**Use case**: Abstracting data access

```python
# Repository interface
class PullRequestRepository(ABC):
    @abstractmethod
    def get_by_number(self, repo: str, number: int) -> PullRequest:
        pass
    
    @abstractmethod
    def list(self, repo: str, state: str) -> List[PullRequest]:
        pass

# Implementation
class GitHubPRRepository(PullRequestRepository):
    def get_by_number(self, repo: str, number: int) -> PullRequest:
        # GitHub API implementation
        pass
```

### 4. Template Method Pattern
**Use case**: Base agent with common workflow

```python
class BaseAgent(ABC):
    def execute(self, input_data):
        # Template method
        validated = self.validate(input_data)
        processed = self.process(validated)
        result = self.format(processed)
        return result
    
    @abstractmethod
    def process(self, data):
        # Subclasses implement this
        pass
    
    def validate(self, data):
        # Common validation
        return data
    
    def format(self, result):
        # Common formatting
        return result
```

### 5. Observer Pattern
**Use case**: Progress notifications

```python
class ProgressObserver(ABC):
    @abstractmethod
    def update(self, progress: int, message: str):
        pass

class ConsoleProgressObserver(ProgressObserver):
    def update(self, progress: int, message: str):
        print(f"[{progress}%] {message}")

class ReviewOrchestrator:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer: ProgressObserver):
        self._observers.append(observer)
    
    def notify(self, progress: int, message: str):
        for observer in self._observers:
            observer.update(progress, message)
```

## 🔍 Code Quality Standards

### Naming Conventions

```python
# Classes: PascalCase
class CodeReviewerAgent:
    pass

# Functions/Methods: snake_case
def analyze_pull_request():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILES_PER_REVIEW = 50

# Private members: _leading_underscore
class Agent:
    def __init__(self):
        self._llm = None
    
    def _internal_method(self):
        pass

# Protected (convention): _leading_underscore
# Public: no underscore
```

### Type Hints

```python
from typing import List, Dict, Optional, Any

# Always use type hints
def review_code(
    pull_request: PullRequest,
    llm: LLMProvider,
    max_files: int = 50
) -> ReviewResult:
    issues: List[Issue] = []
    metadata: Dict[str, Any] = {}
    return ReviewResult(issues=issues, metadata=metadata)

# Use Optional for nullable values
def get_file_content(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    return read_file(path)
```

### Docstrings

```python
def analyze_pull_request(
    repository: str,
    pr_number: int,
    include_tests: bool = True
) -> ReviewResult:
    """
    Analyze a GitHub pull request for code quality issues.
    
    This function fetches the PR data, analyzes all changed files,
    and returns a comprehensive review result with identified issues.
    
    Args:
        repository: Repository in format "owner/repo"
        pr_number: Pull request number
        include_tests: Whether to analyze test files (default: True)
    
    Returns:
        ReviewResult containing issues, summary, and recommendations
    
    Raises:
        GitHubClientError: If PR cannot be fetched
        AnalyzerError: If analysis fails
        
    Example:
        >>> result = analyze_pull_request("microsoft/vscode", 12345)
        >>> print(f"Found {result.total_issues} issues")
    """
    pass
```

### Error Handling

```python
# Good error handling
def fetch_pull_request(repo: str, pr_number: int) -> PullRequest:
    try:
        github = GitHubClient(token)
        pr = github.get_pull_request(repo, pr_number)
        return pr
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise
    except RateLimitError as e:
        logger.warning(f"Rate limit hit: {e}")
        # Retry with backoff
        time.sleep(60)
        return fetch_pull_request(repo, pr_number)
    except GitHubClientError as e:
        logger.error(f"GitHub error: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise CodeReviewError(f"Failed to fetch PR: {e}") from e
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed information for debugging")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error messages")
logger.critical("Critical issues")

# Include context
logger.info(
    "Reviewing pull request",
    extra={
        "repository": repo,
        "pr_number": pr_number,
        "files": len(files)
    }
)
```

## 🧪 Testing Best Practices

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch

class TestGitHubClient:
    @pytest.fixture
    def client(self):
        return GitHubClient(token="test-token")
    
    def test_get_pull_request(self, client):
        # Arrange
        repo = "owner/repo"
        pr_number = 123
        
        # Act
        with patch.object(client, '_client') as mock_client:
            mock_client.get_repo().get_pull.return_value = Mock(
                number=123,
                title="Test PR"
            )
            result = client.get_pull_request(repo, pr_number)
        
        # Assert
        assert result.number == 123
        assert result.title == "Test PR"
    
    def test_invalid_token_raises_error(self):
        # Arrange & Act & Assert
        with pytest.raises(AuthenticationError):
            GitHubClient(token="invalid")
```

### Integration Tests

```python
@pytest.mark.integration
class TestEndToEndReview:
    def test_full_review_workflow(self):
        # Setup
        settings = get_settings()
        github = GitHubClient(settings.github_token)
        llm = GeminiProvider(settings.google_api_key)
        orchestrator = ReviewOrchestrator(github, llm)
        
        # Execute
        result = orchestrator.review_pull_request(
            "test-owner/test-repo",
            1
        )
        
        # Verify
        assert result.status == ReviewStatus.COMPLETED
        assert result.total_issues >= 0
```

## 📊 Performance Optimization

### Caching

```python
from functools import lru_cache
from typing import Dict
import time

class CachedLLMProvider:
    def __init__(self, provider: LLMProvider):
        self._provider = provider
        self._cache: Dict[str, tuple[str, float]] = {}
        self._ttl = 3600  # 1 hour
    
    def generate(self, prompt: str) -> str:
        cache_key = hash(prompt)
        
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._ttl:
                return result
        
        result = self._provider.generate(prompt)
        self._cache[cache_key] = (result, time.time())
        return result
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def analyze_files_parallel(
    files: List[CodeChange],
    analyzer: CodeAnalyzer,
    max_workers: int = 4
) -> Dict[str, List[Issue]]:
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(analyzer.analyze, file): file
            for file in files
        }
        
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                issues = future.result()
                results[file.filename] = issues
            except Exception as e:
                logger.error(f"Failed to analyze {file.filename}: {e}")
    
    return results
```

### Rate Limiting

```python
from tenacity import retry, wait_exponential, stop_after_attempt

class RateLimitedClient:
    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(3)
    )
    def make_request(self, endpoint: str):
        response = requests.get(endpoint)
        
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        
        return response
```

## 🔒 Security Best Practices

### 1. API Key Management

```python
# Good - from environment
api_key = os.getenv("GOOGLE_API_KEY")

# Good - from secure config
from config import get_settings
settings = get_settings()
api_key = settings.google_api_key

# Bad - hardcoded
api_key = "AIzaSy..."  # Never do this!
```

### 2. Input Validation

```python
def validate_repository_name(repo: str) -> str:
    if not re.match(r'^[\w\-]+/[\w\-]+$', repo):
        raise ValidationError(f"Invalid repository format: {repo}")
    return repo

def validate_pr_number(pr_number: int) -> int:
    if pr_number < 1:
        raise ValidationError(f"PR number must be positive: {pr_number}")
    return pr_number
```

### 3. Sensitive Data Masking

```python
def mask_sensitive_data(text: str) -> str:
    # Mask API keys
    text = re.sub(
        r'(api[_-]?key\s*[:=]\s*)["\']?[A-Za-z0-9]{20,}["\']?',
        r'\1***MASKED***',
        text,
        flags=re.IGNORECASE
    )
    
    # Mask tokens
    text = re.sub(
        r'(token\s*[:=]\s*)["\']?[A-Za-z0-9]{20,}["\']?',
        r'\1***MASKED***',
        text,
        flags=re.IGNORECASE
    )
    
    return text
```

## 📝 Git Workflow

### Commit Messages

```
Format: <type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Examples:
feat(github): add support for draft PRs
fix(llm): handle timeout errors gracefully
docs(readme): update installation instructions
refactor(agents): extract common agent logic to base class
```

### Branch Strategy

```
main - Production-ready code
develop - Integration branch
feature/* - New features
fix/* - Bug fixes
refactor/* - Code improvements

Example:
feature/crewai-integration
fix/rate-limit-handling
refactor/agent-architecture
```

## 🎯 Code Review Checklist

Before submitting code:

- [ ] Code follows SOLID principles
- [ ] Design patterns properly applied
- [ ] Type hints added
- [ ] Docstrings complete
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Tests written
- [ ] Tests passing
- [ ] No hardcoded secrets
- [ ] Input validated
- [ ] Performance considered
- [ ] Documentation updated

## 💡 Common Pitfalls to Avoid

1. **God Objects**: Classes that do too much
2. **Tight Coupling**: Direct dependencies on concrete classes
3. **Magic Numbers**: Use named constants
4. **Catching Generic Exceptions**: Be specific
5. **Ignoring Type Hints**: Always use them
6. **Poor Naming**: Be descriptive
7. **No Tests**: Test as you go
8. **Hardcoded Configuration**: Use settings
9. **No Logging**: Log important operations
10. **Premature Optimization**: Make it work, then optimize

## 🚀 Conclusion

Following these best practices will result in:
- ✅ Maintainable code
- ✅ Scalable architecture
- ✅ Testable components
- ✅ Professional quality
- ✅ Easy collaboration
- ✅ Future-proof design

**Remember**: Write code that your future self will thank you for!
