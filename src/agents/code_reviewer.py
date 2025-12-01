"""Code reviewer agent for general code quality analysis."""

from crewai import Agent
from .base_agent import BaseAgent


class CodeReviewerAgent(BaseAgent):
    """
    Agent specialized in general code quality review.
    
    Responsibilities:
    - Code quality assessment
    - Best practices validation
    - SOLID principles checking
    - Code readability analysis
    - Design pattern suggestions
    """
    
    @property
    def role(self) -> str:
        return "Senior Code Reviewer"
    
    @property
    def goal(self) -> str:
        return (
            "Analyze code changes for quality, maintainability, and adherence to "
            "best practices. Identify code smells, anti-patterns, and suggest improvements."
        )
    
    @property
    def backstory(self) -> str:
        return (
            "You are an experienced software engineer with 15+ years of experience "
            "in code review and software architecture. You have deep knowledge of "
            "SOLID principles, design patterns, and clean code practices across "
            "multiple programming languages. Your reviews are thorough, constructive, "
            "and focused on improving code quality and maintainability."
        )
    
    def create_agent(self) -> Agent:
        """Create the code reviewer agent."""
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            verbose=self.verbose,
            allow_delegation=self.allow_delegation,
            max_iter=15,
        )


# TODO: Implement these agents following the same pattern

class SecurityAnalyzerAgent(BaseAgent):
    """Agent specialized in security vulnerability detection."""
    
    @property
    def role(self) -> str:
        return "Security Analyst"
    
    @property
    def goal(self) -> str:
        return (
            "Identify security vulnerabilities, potential exploits, and insecure "
            "coding practices in code changes."
        )
    
    @property
    def backstory(self) -> str:
        return (
            "You are a cybersecurity expert specializing in application security "
            "and secure coding practices. You have extensive experience with OWASP "
            "Top 10, common vulnerabilities (SQL injection, XSS, CSRF, etc.), and "
            "security best practices across different tech stacks."
        )
    
    def create_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            verbose=self.verbose,
            allow_delegation=self.allow_delegation,
        )


class PerformanceAnalyzerAgent(BaseAgent):
    """Agent specialized in performance analysis."""
    
    @property
    def role(self) -> str:
        return "Performance Engineer"
    
    @property
    def goal(self) -> str:
        return (
            "Identify performance bottlenecks, inefficient algorithms, and "
            "resource-intensive operations in code changes."
        )
    
    @property
    def backstory(self) -> str:
        return (
            "You are a performance optimization specialist with deep knowledge of "
            "algorithmic complexity, memory management, and system performance. "
            "You can identify inefficient code patterns and suggest optimizations."
        )
    
    def create_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            verbose=self.verbose,
            allow_delegation=self.allow_delegation,
        )


class SuggestionGeneratorAgent(BaseAgent):
    """Agent specialized in generating actionable improvement suggestions."""
    
    @property
    def role(self) -> str:
        return "Code Improvement Specialist"
    
    @property
    def goal(self) -> str:
        return (
            "Generate actionable, prioritized suggestions for code improvements "
            "based on identified issues."
        )
    
    @property
    def backstory(self) -> str:
        return (
            "You are an expert at translating technical issues into clear, "
            "actionable recommendations. You understand how to prioritize "
            "improvements and provide specific, implementable solutions."
        )
    
    def create_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            verbose=self.verbose,
            allow_delegation=self.allow_delegation,
        )
