"""Value object for review status."""

from enum import Enum


class ReviewStatus(str, Enum):
    """Enum representing the status of a code review."""
    
    PENDING = "pending"  # Review not started
    IN_PROGRESS = "in_progress"  # Currently being reviewed
    COMPLETED = "completed"  # Review completed successfully
    FAILED = "failed"  # Review failed with errors
    PARTIAL = "partial"  # Review partially completed
    SKIPPED = "skipped"  # Review skipped
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Return representation."""
        return f"ReviewStatus.{self.name}"
    
    @property
    def emoji(self) -> str:
        """Return emoji representation for display."""
        return {
            ReviewStatus.PENDING: "⏳",
            ReviewStatus.IN_PROGRESS: "🔄",
            ReviewStatus.COMPLETED: "✅",
            ReviewStatus.FAILED: "❌",
            ReviewStatus.PARTIAL: "⚠️",
            ReviewStatus.SKIPPED: "⏭️",
        }[self]
    
    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        return self in {ReviewStatus.COMPLETED, ReviewStatus.FAILED, ReviewStatus.SKIPPED}
