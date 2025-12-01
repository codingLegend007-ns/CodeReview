"""Base agent class for all CrewAI agents."""

from abc import ABC, abstractmethod
from typing import Optional
from crewai import Agent


class BaseAgent(ABC):
    """
    Abstract base class for all review agents.
    
    Follows Template Method pattern for agent creation.
    """
    
    def __init__(
        self,
        llm: any,
        verbose: bool = False,
        allow_delegation: bool = False
    ):
        """
        Initialize base agent.
        
        Args:
            llm: Language model instance
            verbose: Enable verbose output
            allow_delegation: Allow agent to delegate tasks
        """
        self.llm = llm
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self._agent: Optional[Agent] = None
    
    @abstractmethod
    def create_agent(self) -> Agent:
        """
        Create and return the CrewAI agent.
        
        Returns:
            Configured Agent instance
        """
        pass
    
    def get_agent(self) -> Agent:
        """
        Get or create the agent instance (lazy initialization).
        
        Returns:
            Agent instance
        """
        if self._agent is None:
            self._agent = self.create_agent()
        return self._agent
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Return the agent's role."""
        pass
    
    @property
    @abstractmethod
    def goal(self) -> str:
        """Return the agent's goal."""
        pass
    
    @property
    @abstractmethod
    def backstory(self) -> str:
        """Return the agent's backstory."""
        pass
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}(role='{self.role}')"
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"{self.__class__.__name__}(role='{self.role}', verbose={self.verbose})"
