"""Domain entity representing a review result."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from .issue import Issue
from .pull_request import PullRequest
from ..value_objects.review_status import ReviewStatus
from ..value_objects.severity import Severity


@dataclass
class ReviewResult:
    """Represents the result of a code review."""
    
    pull_request: PullRequest
    status: ReviewStatus
    issues: List[Issue] = field(default_factory=list)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    reviewed_files: int = 0
    skipped_files: int = 0
    total_issues: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    info_issues: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate issue counts from issues list."""
        if self.issues:
            self._update_issue_counts()
    
    def _update_issue_counts(self):
        """Update issue counts based on issues list."""
        self.total_issues = len(self.issues)
        self.critical_issues = sum(1 for i in self.issues if i.severity == Severity.CRITICAL)
        self.high_issues = sum(1 for i in self.issues if i.severity == Severity.HIGH)
        self.medium_issues = sum(1 for i in self.issues if i.severity == Severity.MEDIUM)
        self.low_issues = sum(1 for i in self.issues if i.severity == Severity.LOW)
        self.info_issues = sum(1 for i in self.issues if i.severity == Severity.INFO)
    
    def add_issue(self, issue: Issue):
        """Add an issue to the review result."""
        self.issues.append(issue)
        self._update_issue_counts()
    
    def add_issues(self, issues: List[Issue]):
        """Add multiple issues to the review result."""
        self.issues.extend(issues)
        self._update_issue_counts()
    
    def complete(self):
        """Mark review as completed and calculate duration."""
        self.status = ReviewStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def fail(self, error_message: str):
        """Mark review as failed."""
        self.status = ReviewStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.metadata["error"] = error_message
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if review found critical issues."""
        return self.critical_issues > 0
    
    @property
    def issues_by_severity(self) -> Dict[Severity, List[Issue]]:
        """Group issues by severity."""
        result = {severity: [] for severity in Severity}
        for issue in self.issues:
            result[issue.severity].append(issue)
        return result
    
    @property
    def issues_by_category(self) -> Dict[str, List[Issue]]:
        """Group issues by category."""
        result: Dict[str, List[Issue]] = {}
        for issue in self.issues:
            if issue.category not in result:
                result[issue.category] = []
            result[issue.category].append(issue)
        return result
    
    @property
    def issues_by_file(self) -> Dict[str, List[Issue]]:
        """Group issues by file."""
        result: Dict[str, List[Issue]] = {}
        for issue in self.issues:
            if issue.file_path not in result:
                result[issue.file_path] = []
            result[issue.file_path].append(issue)
        return result
    
    @property
    def severity_summary(self) -> str:
        """Return formatted severity summary."""
        parts = []
        if self.critical_issues:
            parts.append(f"{Severity.CRITICAL.emoji} {self.critical_issues} Critical")
        if self.high_issues:
            parts.append(f"{Severity.HIGH.emoji} {self.high_issues} High")
        if self.medium_issues:
            parts.append(f"{Severity.MEDIUM.emoji} {self.medium_issues} Medium")
        if self.low_issues:
            parts.append(f"{Severity.LOW.emoji} {self.low_issues} Low")
        if self.info_issues:
            parts.append(f"{Severity.INFO.emoji} {self.info_issues} Info")
        return " | ".join(parts) if parts else "No issues found"
    
    def to_dict(self) -> dict:
        """Convert review result to dictionary."""
        return {
            "pull_request": self.pull_request.to_dict(),
            "status": self.status.value,
            "summary": self.summary,
            "recommendations": self.recommendations,
            "reviewed_files": self.reviewed_files,
            "skipped_files": self.skipped_files,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "high_issues": self.high_issues,
            "medium_issues": self.medium_issues,
            "low_issues": self.low_issues,
            "info_issues": self.info_issues,
            "severity_summary": self.severity_summary,
            "issues": [issue.to_dict() for issue in self.issues],
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }
    
    def __str__(self) -> str:
        """Return string representation."""
        return (
            f"Review of {self.pull_request} - {self.status.value.upper()}\n"
            f"Issues: {self.severity_summary}\n"
            f"Duration: {self.duration_seconds:.1f}s"
        )
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"ReviewResult(pr={self.pull_request.number}, status={self.status}, issues={self.total_issues})"
