"""Value object for issue severity levels."""

from enum import Enum


class Severity(str, Enum):
    """Enum representing the severity level of code issues."""
    
    CRITICAL = "critical"  # Security vulnerabilities, breaking changes
    HIGH = "high"  # Major bugs, significant performance issues
    MEDIUM = "medium"  # Code quality issues, minor bugs
    LOW = "low"  # Style issues, minor improvements
    INFO = "info"  # Informational suggestions
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Return representation."""
        return f"Severity.{self.name}"
    
    @property
    def emoji(self) -> str:
        """Return emoji representation for display."""
        return {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "🟠",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "🟢",
            Severity.INFO: "🔵",
        }[self]
    
    @property
    def priority(self) -> int:
        """Return numeric priority for sorting."""
        return {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1,
        }[self]
