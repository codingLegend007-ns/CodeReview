"""Domain entity representing a pull request."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from .code_change import CodeChange


@dataclass
class PullRequest:
    """Represents a GitHub pull request."""
    
    number: int
    title: str
    description: Optional[str]
    author: str
    repository: str
    base_branch: str
    head_branch: str
    state: str  # open, closed, merged
    created_at: datetime
    updated_at: datetime
    url: str
    changes: List[CodeChange] = field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0
    total_changes: int = 0
    changed_files_count: int = 0
    
    def __post_init__(self):
        """Calculate totals from changes if not provided."""
        if not self.changes:
            return
        
        if self.total_additions == 0:
            self.total_additions = sum(change.additions for change in self.changes)
        
        if self.total_deletions == 0:
            self.total_deletions = sum(change.deletions for change in self.changes)
        
        if self.total_changes == 0:
            self.total_changes = sum(change.changes for change in self.changes)
        
        if self.changed_files_count == 0:
            self.changed_files_count = len(self.changes)
    
    @property
    def significant_changes(self) -> List[CodeChange]:
        """Return only significant changes that should be reviewed."""
        return [change for change in self.changes if change.is_significant]
    
    @property
    def size_category(self) -> str:
        """Categorize PR size."""
        total = self.total_changes
        if total < 50:
            return "small"
        elif total < 200:
            return "medium"
        elif total < 500:
            return "large"
        else:
            return "extra-large"
    
    @property
    def summary(self) -> str:
        """Return PR summary."""
        return (
            f"PR #{self.number}: {self.title}\n"
            f"Author: {self.author}\n"
            f"Branch: {self.head_branch} → {self.base_branch}\n"
            f"Files: {self.changed_files_count} | "
            f"Changes: +{self.total_additions}/-{self.total_deletions}\n"
            f"Size: {self.size_category}"
        )
    
    def get_changes_by_language(self, language: str) -> List[CodeChange]:
        """Get changes filtered by programming language."""
        return [change for change in self.changes if change.language == language]
    
    def to_dict(self) -> dict:
        """Convert PR to dictionary."""
        return {
            "number": self.number,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "repository": self.repository,
            "base_branch": self.base_branch,
            "head_branch": self.head_branch,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "url": self.url,
            "total_additions": self.total_additions,
            "total_deletions": self.total_deletions,
            "total_changes": self.total_changes,
            "changed_files_count": self.changed_files_count,
            "size_category": self.size_category,
            "changes": [change.to_dict() for change in self.changes],
        }
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"PR #{self.number}: {self.title}"
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"PullRequest(number={self.number}, title='{self.title}', files={self.changed_files_count})"
