"""Tasks for CrewAI agents."""

import textwrap
from typing import Any, Dict, List, TYPE_CHECKING

try:
    from crewai import Task
except ImportError as import_error:  # pragma: no cover - defensive import
    Task = None
    _TASK_IMPORT_ERROR = import_error
else:
    _TASK_IMPORT_ERROR = None

from ..core.entities import PullRequest, CodeChange

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from crewai import Task as CrewTaskType
else:
    CrewTaskType = Any


def create_code_review_task(
    agent: any,
    pull_request: PullRequest,
    code_changes: List[CodeChange],
    context: Dict[str, Any] = None
) -> "CrewTaskType":
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
    - Class or function name
    - Line numbers (reference the primary line that needs attention)
    - Issue description
    - Severity (critical, high, medium, low, info)
    - Suggested fix
    All comments must be concise, actionable, and understandable to a broad engineering audience.
    """
    
    expected_output = """
    A structured analysis containing:
    1. Overall code quality assessment
    2. List of identified issues with severity levels, each citing file path, class or function name, and line number
    3. Specific recommendations for each issue
    4. Priority order for fixes
    """
    
    if Task is None:
        raise ImportError(
            "crewai package is required to build review tasks."
        ) from _TASK_IMPORT_ERROR

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
) -> "CrewTaskType":
    """Create a security analysis task."""
    if Task is None:
        raise ImportError(
            "crewai package is required to build review tasks."
        ) from _TASK_IMPORT_ERROR
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
    For every finding, include the file path, class or function name, and the relevant line number.
    """
    
    expected_output = """
    Security analysis report with:
    1. List of security vulnerabilities (file path, class/function, and line number for each)
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
) -> "CrewTaskType":
    """Create a performance analysis task."""
    if Task is None:
        raise ImportError(
            "crewai package is required to build review tasks."
        ) from _TASK_IMPORT_ERROR
    description = f"""
    Analyze pull request #{pull_request.number} for performance issues.
    
    Check for:
    1. Inefficient algorithms (O(n²) or worse)
    2. Memory leaks
    3. Unnecessary database queries (N+1 problem)
    4. Blocking operations
    5. Resource-intensive operations
    6. Missing caching opportunities
    Document every issue with the file path, class or function name, and the precise line number.
    """
    
    expected_output = """
    Performance analysis report with:
    1. Identified performance bottlenecks (file path, class/function, line number)
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
) -> "CrewTaskType":
    """Create a suggestion generation task."""
    if Task is None:
        raise ImportError(
            "crewai package is required to build review tasks."
        ) from _TASK_IMPORT_ERROR
    summary_sections: List[str] = []
    for name, output in review_results.items():
        if not output:
            continue
        title = name.replace("_", " ").title()
        formatted_output = (
            output if len(output) <= 1200
            else textwrap.shorten(output, width=1200, placeholder="... [truncated]")
        )
        summary_sections.append(f"### {title}\n{formatted_output}")

    prior_findings = "\n\n".join(summary_sections) if summary_sections else "No prior findings were provided."

    description = f"""
    Based on the review results, generate actionable improvement suggestions.

    Prior analyses:
    {prior_findings}

    Consolidate findings from:
    - Code quality review
    - Security analysis
    - Performance analysis

    Generate:
    1. Prioritized list of improvements (include file path, class/function, and line number where applicable)
    2. Specific implementation guidance
    3. Code examples where applicable
    4. Estimated effort for each suggestion
    """

    expected_output = """
    Structured improvement plan with:
    1. Top 5 critical improvements, each referencing file path, class/function, and line number
    2. Detailed action items
    3. Implementation examples
    4. Priority and effort estimates
    """

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context,
    )
