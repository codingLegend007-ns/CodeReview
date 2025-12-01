"""Domain entity representing a code issue."""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from ..value_objects.severity import Severity

"""
this is just new comment for testing.

New update for new PR testing.
"""


@dataclass
class Issue:
    """Represents a code issue found during review."""
    
    title: str
    description: str
    severity: Severity
    file_path: str
    line_number: Optional[int] = None
    line_range: Optional[tuple[int, int]] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    category: str = "general"  # e.g., "security", "performance", "quality"
    tags: List[str] = field(default_factory=list)
    detected_by: str = "unknown"  # Agent that detected the issue
    confidence: float = 1.0  # Confidence score (0.0 to 1.0)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate issue data after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        if self.line_number and self.line_number < 1:
            raise ValueError("Line number must be positive")
        
        if self.line_range:
            start, end = self.line_range
            if start < 1 or end < start:
                raise ValueError("Invalid line range")
    
    @property
    def location(self) -> str:
        """Return formatted location string."""
        if self.line_range:
            return f"{self.file_path}:{self.line_range[0]}-{self.line_range[1]}"
        elif self.line_number:
            return f"{self.file_path}:{self.line_number}"
        return self.file_path
    
    @property
    def priority_score(self) -> float:
        """Calculate priority score for sorting."""
        return self.severity.priority * self.confidence
    
    def to_dict(self) -> dict:
        """Convert issue to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "line_range": self.line_range,
            "code_snippet": self.code_snippet,
            "suggestion": self.suggestion,
            "category": self.category,
            "tags": self.tags,
            "detected_by": self.detected_by,
            "confidence": self.confidence,
            "location": self.location,
            "priority_score": self.priority_score,
            "created_at": self.created_at.isoformat(),
        }
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"[{self.severity.emoji} {self.severity.value.upper()}] {self.title} at {self.location}"
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"Issue(title='{self.title}', severity={self.severity}, location='{self.location}')"
