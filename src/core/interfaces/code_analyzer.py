"""Abstract interface for code analyzers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..entities.code_change import CodeChange
from ..entities.issue import Issue


class CodeAnalyzer(ABC):
    """Abstract base class for code analyzers."""
    
    @abstractmethod
    def analyze(
        self,
        code_change: CodeChange,
        context: Dict[str, Any] = None
    ) -> List[Issue]:
        """
        Analyze a code change and return issues.
        
        Args:
            code_change: The code change to analyze
            context: Additional context for analysis
            
        Returns:
            List of issues found
            
        Raises:
            AnalyzerError: If analysis fails
        """
        pass
    
    @abstractmethod
    def analyze_batch(
        self,
        code_changes: List[CodeChange],
        context: Dict[str, Any] = None
    ) -> Dict[str, List[Issue]]:
        """
        Analyze multiple code changes.
        
        Args:
            code_changes: List of code changes to analyze
            context: Additional context for analysis
            
        Returns:
            Dictionary mapping file paths to lists of issues
            
        Raises:
            AnalyzerError: If analysis fails
        """
        pass
    
    @property
    @abstractmethod
    def analyzer_name(self) -> str:
        """Return the name of the analyzer."""
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Return list of supported programming languages."""
        pass
    
    def can_analyze(self, code_change: CodeChange) -> bool:
        """
        Check if this analyzer can analyze the given code change.
        
        Args:
            code_change: The code change to check
            
        Returns:
            True if analyzer supports this change
        """
        if code_change.is_binary:
            return False
        
        if not code_change.language:
            return True  # Analyze anyway if language is unknown
        
        return code_change.language.lower() in [
            lang.lower() for lang in self.supported_languages
        ]
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.analyzer_name}"
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"{self.__class__.__name__}(name='{self.analyzer_name}')"
