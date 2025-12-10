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


def _build_allowed_files_text(code_changes: List[CodeChange], *, limit: int = 12) -> str:
    """Return instructions constraining analysis to the actual changed files."""

    files = sorted({change.filename for change in code_changes if getattr(change, "filename", None)})
    if not files:
        return (
            "Only evaluate the files included in the pull request diff. Do not invent new "
            "file paths or extensions."
        )

    display = files[:limit]
    remaining = len(files) - len(display)
    file_lines = "\n".join(f"- {path}" for path in display)
    if remaining > 0:
        file_lines += f"\n- ... (+{remaining} more files)"

    return (
        "Only reference files from this definitive list. Use the paths and extensions "
        "exactly as written; do not mention any other files or languages:\n"
        f"{file_lines}"
    )


def _build_diff_context(
    code_changes: List[CodeChange],
    *,
    max_files: int = 12,
    max_total_chars: int = 10000,
    max_patch_chars: int = 1500,
) -> str:
    """Construct a diff-focused context string limited to PR changes."""

    if not code_changes:
        return "Diff context unavailable (no code changes were supplied)."

    sections: List[str] = []
    total_chars = 0

    for change in code_changes[:max_files]:
        filename = getattr(change, "filename", "<unknown>")
        status = getattr(change, "status", None)
        status_text = getattr(status, "value", str(status) if status else "unknown")
        patch = getattr(change, "patch", None)

        if patch:
            trimmed = patch.strip()
            if len(trimmed) > max_patch_chars:
                trimmed = trimmed[:max_patch_chars].rstrip() + "\n... [diff truncated]"
            diff_block = f"```diff\n{trimmed}\n```"
        else:
            diff_block = "Diff unavailable (binary file or patch not provided)."

        section = (
            f"File: {filename}\n"
            f"Status: {status_text}\n"
            f"{diff_block}"
        )
        section_length = len(section)
        if total_chars + section_length > max_total_chars:
            sections.append("... Additional file diffs omitted to stay within limits.")
            break
        sections.append(section)
        total_chars += section_length

    return "\n\n".join(sections)

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
    allowed_files_text = _build_allowed_files_text(code_changes)

    description = f"""
    Review the following pull request for code quality issues:
    
    PR: #{pull_request.number} - {pull_request.title}
    Repository: {pull_request.repository}
    Files changed: {len(code_changes)}

    {allowed_files_text}

    Focus strictly on the modified lines included in these diff hunks. Do not comment on
    unchanged portions of any file or reference code outside the pull request.

    Diff context:
    {_build_diff_context(code_changes)}
    
    Analyze the code changes for:
    1. Code quality and maintainability
    2. Best practices and coding standards
    3. SOLID principles adherence
    4. Code smells and anti-patterns
    5. Documentation completeness
    
    For each issue, write one or two plain-English sentences that include:
    - File path
    - Class or function name
    - Primary line number that needs attention
    - Clear description of the problem and why it matters
    - Severity (critical, high, medium, low, info)
    - Suggested fix with reference to the applicable coding standard or guideline (e.g., PEP 8, SOLID, company style guide)
    All comments must avoid bullet points and remain concise, actionable, and understandable to any engineer.
        """
    
    expected_output = """
    A structured analysis containing:
    1. Overall code quality assessment written in plain sentences
    2. Identified issues with severity levels, each citing file path, class/function, line number, and relevant coding standard
    3. Specific recommendations for each issue expressed without bullet points
    4. Priority order for fixes using narrative sentences
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
    allowed_files_text = _build_allowed_files_text(code_changes)

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
    {allowed_files_text}

    Focus strictly on the diff hunks provided below. Ignore unchanged code and do not
    reference files outside the pull request.

    Diff context:
    {_build_diff_context(code_changes)}

    For every finding, write one or two sentences that include the file path (from the allowed list), class or function name, relevant line number in the diff, impact, and reference to the applicable security standard (e.g., OWASP Top 10, company policy). Avoid bullet points.
    """
    
    expected_output = """
    Security analysis report with:
    1. Narrative list of security vulnerabilities, each citing file path, class/function, line number, and relevant security standards
    2. Risk level for each vulnerability stated in plain sentences
    3. Potential impact described clearly
    4. Remediation steps expressed in easy-to-understand prose (no bullet points)
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
    allowed_files_text = _build_allowed_files_text(code_changes)

    description = f"""
    Analyze pull request #{pull_request.number} for performance issues.
    
    Check for:
    1. Inefficient algorithms (O(n²) or worse)
    2. Memory leaks
    3. Unnecessary database queries (N+1 problem)
    4. Blocking operations
    5. Resource-intensive operations
    6. Missing caching opportunities
    {allowed_files_text}

    Focus strictly on the diff hunks provided below. Ignore unchanged code and do not
    reference files outside the pull request.

    Diff context:
    {_build_diff_context(code_changes)}

    Document every issue with one or two clear sentences that provide the file path (choose from the allowed list), class or function name, precise line number from the diff, performance impact, and any applicable engineering guideline (e.g., big-O expectations, scalability standards). Do not use bullet points.
    """
    
    expected_output = """
    Performance analysis report with:
    1. Identified performance bottlenecks written as sentences citing file path, class/function, and line number
    2. Algorithmic complexity analysis articulated plainly
    3. Resource usage concerns explained in everyday language
    4. Optimization recommendations described without bullet points, referencing best-practice standards where relevant
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
    1. Prioritized list of improvements (each described in sentences that include file path, class/function, line number, and relevant coding or architectural standards)
    2. Specific implementation guidance explained plainly
    3. Code examples where applicable
    4. Estimated effort for each suggestion using descriptive prose
    """

    expected_output = """
    Structured improvement plan with:
    1. Top 5 critical improvements, each referencing file path, class/function, line number, and applicable standards in sentence form
    2. Detailed action items without bullet formatting
    3. Implementation examples, if needed, introduced within the narrative
    4. Priority and effort estimates expressed as plain sentences
    """

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context,
    )
