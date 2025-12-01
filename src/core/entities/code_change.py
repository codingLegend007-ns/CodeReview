"""Domain entity representing a code change."""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class ChangeType(str, Enum):
    """Type of code change."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class CodeChange:
    """Represents a single file change in a pull request."""
    
    filename: str
    status: ChangeType
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None
    content: Optional[str] = None
    previous_filename: Optional[str] = None
    language: Optional[str] = None
    is_binary: bool = False
    
    def __post_init__(self):
        """Validate change data."""
        if self.additions < 0 or self.deletions < 0 or self.changes < 0:
            raise ValueError("Additions, deletions, and changes must be non-negative")
        
        if self.is_binary and self.patch:
            self.patch = None  # Binary files shouldn't have patches
    
    @property
    def change_summary(self) -> str:
        """Return summary of changes."""
        if self.status == ChangeType.DELETED:
            return f"Deleted {self.filename}"
        elif self.status == ChangeType.ADDED:
            return f"Added {self.filename} (+{self.additions} lines)"
        elif self.status == ChangeType.RENAMED:
            return f"Renamed {self.previous_filename} → {self.filename}"
        else:
            return f"Modified {self.filename} (+{self.additions}/-{self.deletions})"
    
    @property
    def is_significant(self) -> bool:
        """Determine if this change is significant enough to review."""
        if self.is_binary:
            return False
        return self.changes > 0 and not self._is_excluded_file()
    
    def _is_excluded_file(self) -> bool:
        """Check if file should be excluded from review."""
        excluded_extensions = {'.md', '.txt', '.json', '.yaml', '.yml', '.lock'}
        excluded_patterns = {'package-lock.json', 'yarn.lock', 'Pipfile.lock'}
        
        if any(self.filename.endswith(ext) for ext in excluded_extensions):
            return True
        
        if any(pattern in self.filename for pattern in excluded_patterns):
            return True
        
        return False
    
    def to_dict(self) -> dict:
        """Convert change to dictionary."""
        return {
            "filename": self.filename,
            "status": self.status.value,
            "additions": self.additions,
            "deletions": self.deletions,
            "changes": self.changes,
            "previous_filename": self.previous_filename,
            "language": self.language,
            "is_binary": self.is_binary,
            "change_summary": self.change_summary,
            "is_significant": self.is_significant,
        }
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.change_summary
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"CodeChange(filename='{self.filename}', status={self.status}, changes={self.changes})"
