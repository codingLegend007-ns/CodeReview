"""Tasks for CrewAI agents."""

from crewai import Task
from typing import Dict, Any, List
from ..core.entities import PullRequest, CodeChange


def create_code_review_task(
    agent: any,
    pull_request: PullRequest,
    code_changes: List[CodeChange],
    context: Dict[str, Any] = None
) -> Task:
    """
    Create a code review task.
    
    Args:
        agent: The agent to execute the task
        pull_request: Pull request to review
        code_changes: List of code changes
        context: Additional context
        
    Returns:
        Task instance
    """
    description = f"""
    Review the following pull request for code quality issues:
    
    PR: #{pull_request.number} - {pull_request.title}
    Repository: {pull_request.repository}
    Files changed: {len(code_changes)}
    
    Analyze the code changes for:
    1. Code quality and maintainability
    2. Best practices and coding standards
    3. SOLID principles adherence
    4. Code smells and anti-patterns
    5. Documentation completeness
    
    For each file, identify specific issues with:
    - File path
    - Line numbers
    - Issue description
    - Severity (critical, high, medium, low, info)
    - Suggested fix
    """
    
    expected_output = """
    A structured analysis containing:
    1. Overall code quality assessment
    2. List of identified issues with severity levels
    3. Specific recommendations for each issue
    4. Priority order for fixes
    """
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )


def create_security_analysis_task(
    agent: any,
    pull_request: PullRequest,
    code_changes: List[CodeChange],
    context: Dict[str, Any] = None
) -> Task:
    """Create a security analysis task."""
    description = f"""
    Perform security analysis on pull request #{pull_request.number}.
    
    Check for:
    1. SQL injection vulnerabilities
    2. XSS vulnerabilities
    3. CSRF vulnerabilities
    4. Authentication/authorization issues
    5. Sensitive data exposure
    6. Insecure dependencies
    7. Hardcoded secrets
    8. Input validation issues
    """
    
    expected_output = """
    Security analysis report with:
    1. List of security vulnerabilities
    2. Risk level for each vulnerability
    3. Potential impact
    4. Remediation steps
    """
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )


def create_performance_analysis_task(
    agent: any,
    pull_request: PullRequest,
    code_changes: List[CodeChange],
    context: Dict[str, Any] = None
) -> Task:
    """Create a performance analysis task."""
    description = f"""
    Analyze pull request #{pull_request.number} for performance issues.
    
    Check for:
    1. Inefficient algorithms (O(n²) or worse)
    2. Memory leaks
    3. Unnecessary database queries (N+1 problem)
    4. Blocking operations
    5. Resource-intensive operations
    6. Missing caching opportunities
    """
    
    expected_output = """
    Performance analysis report with:
    1. Identified performance bottlenecks
    2. Algorithmic complexity analysis
    3. Resource usage concerns
    4. Optimization recommendations
    """
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )


def create_suggestion_generation_task(
    agent: any,
    review_results: Dict[str, Any],
    context: Dict[str, Any] = None
) -> Task:
    """Create a suggestion generation task."""
    description = f"""
    Based on the review results, generate actionable improvement suggestions.
    
    Consolidate findings from:
    - Code quality review
    - Security analysis
    - Performance analysis
    
    Generate:
    1. Prioritized list of improvements
    2. Specific implementation guidance
    3. Code examples where applicable
    4. Estimated effort for each suggestion
    """
    
    expected_output = """
    Structured improvement plan with:
    1. Top 5 critical improvements
    2. Detailed action items
    3. Implementation examples
    4. Priority and effort estimates
    """
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )
