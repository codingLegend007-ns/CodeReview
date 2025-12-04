"""CrewAI orchestration for running multi-agent code reviews."""

from __future__ import annotations

import textwrap
from pathlib import Path

from typing import Any, Dict, List, Optional

try:
	from crewai import Crew, Process
except ImportError as import_error:  # pragma: no cover - defensive import
	Crew = None
	Process = None
	_CREW_IMPORT_ERROR = import_error
else:
	_CREW_IMPORT_ERROR = None

try:
	from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError as import_error:  # pragma: no cover - defensive import
	ChatGoogleGenerativeAI = None
	_LANGCHAIN_IMPORT_ERROR = import_error
else:
	_LANGCHAIN_IMPORT_ERROR = None

from ..agents.code_reviewer import (
	CodeReviewerAgent,
	PerformanceAnalyzerAgent,
	SecurityAnalyzerAgent,
	SuggestionGeneratorAgent,
)
from ..core.entities.pull_request import PullRequest
from ..tasks.review_tasks import (
	create_code_review_task,
	create_performance_analysis_task,
	create_security_analysis_task,
	create_suggestion_generation_task,
)


def create_crewai_llm(
	llm_config: Dict[str, Any],
	*,
	temperature: float = 0.2,
	max_output_tokens: Optional[int] = None,
	**kwargs: Any,
) -> Any:
	"""Create a CrewAI-compatible LLM instance from configuration."""

	provider = llm_config.get("provider")
	model = llm_config.get("model")
	api_key = llm_config.get("api_key")

	if not provider or not api_key:
		raise ValueError("LLM configuration must include provider and api_key")

	if provider == "gemini":
		if ChatGoogleGenerativeAI is None:
			raise ImportError(
				"langchain-google-genai package is required for Gemini CrewAI integration."
			) from _LANGCHAIN_IMPORT_ERROR
		llm_kwargs = {
			"model": model or "gemini-pro",
			"google_api_key": api_key,
			"temperature": temperature,
			"convert_system_message_to_human": True,
		}
		if max_output_tokens is not None:
			llm_kwargs["max_output_tokens"] = max_output_tokens
		llm_kwargs.update(kwargs)
		return ChatGoogleGenerativeAI(**llm_kwargs)

	if provider == "grok":
		raise NotImplementedError(
			"CrewAI orchestration for the Grok provider is not implemented yet."
		)

	raise ValueError(f"Unsupported LLM provider for CrewAI: {provider}")


class ReviewOrchestrator:
	"""Coordinates CrewAI agents to analyze pull requests."""

	def __init__(self, llm: Any, *, verbose: bool = False):
		if Crew is None:
			raise ImportError(
				"crewai package is required for multi-agent orchestration."
			) from _CREW_IMPORT_ERROR
		self.llm = llm
		self.verbose = verbose
		self._agents: Optional[Dict[str, Any]] = None

	def run_review(
		self,
		pull_request: PullRequest,
		*,
		max_files: Optional[int] = None,
	) -> Dict[str, Any]:
		"""Execute the multi-agent review workflow."""

		significant_changes = list(pull_request.significant_changes)
		total_significant = len(significant_changes)

		if not significant_changes:
			raise ValueError("No significant code changes available for review.")

		if max_files is not None and max_files > 0:
			significant_changes = significant_changes[:max_files]

		agents = self._get_agents()

		sections: List[Dict[str, Any]] = []
		intermediate_results: Dict[str, str] = {}
		allowed_filenames = sorted({change.filename for change in significant_changes})

		workflow_plan = [
			(
				"code_review",
				"Code Quality Review",
				agents["code"],
				create_code_review_task,
			),
			(
				"security_analysis",
				"Security Analysis",
				agents["security"],
				create_security_analysis_task,
			),
			(
				"performance_analysis",
				"Performance Analysis",
				agents["performance"],
				create_performance_analysis_task,
			),
		]

		for key, label, agent, task_factory in workflow_plan:
			task = task_factory(agent, pull_request, significant_changes)
			output = self._execute_task(agent, task)
			intermediate_results[key] = output
			polished_output = self._polish_output(label, output, allowed_filenames=allowed_filenames)
			sections.append({
				"key": key,
				"label": label,
				"output": polished_output,
				"raw_output": output,
			})

		suggestion_task = create_suggestion_generation_task(
			agents["suggestion"],
			intermediate_results,
		)
		suggestion_output = self._execute_task(agents["suggestion"], suggestion_task)
		intermediate_results["suggestions"] = suggestion_output
		polished_suggestion = self._polish_output(
			"Improvement Suggestions",
			suggestion_output,
			allowed_filenames=allowed_filenames,
		)
		sections.append({
			"key": "suggestions",
			"label": "Improvement Suggestions",
			"output": polished_suggestion,
			"raw_output": suggestion_output,
		})

		return {
			"sections": sections,
			"metadata": {
				"files_analyzed": len(significant_changes),
				"files_available": total_significant,
				"agents_run": [section["label"] for section in sections],
			},
			"raw_results": intermediate_results,
		}

	def _get_agents(self) -> Dict[str, Any]:
		"""Instantiate CrewAI agents if needed."""

		if self._agents is None:
			self._agents = {
				"code": CodeReviewerAgent(self.llm, verbose=self.verbose).get_agent(),
				"security": SecurityAnalyzerAgent(self.llm, verbose=self.verbose).get_agent(),
				"performance": PerformanceAnalyzerAgent(self.llm, verbose=self.verbose).get_agent(),
				"suggestion": SuggestionGeneratorAgent(self.llm, verbose=self.verbose).get_agent(),
			}
		return self._agents

	def _execute_task(self, agent: Any, task: Any) -> str:
		"""Run a CrewAI task with the provided agent and return output."""

		crew = Crew(
			agents=[agent],
			tasks=[task],
			process=Process.sequential,
			verbose=self.verbose,
		)

		result = crew.kickoff()

		output = getattr(task, "output", None)
		if output:
			if hasattr(output, "raw"):
				return output.raw
			return str(output)

		if isinstance(result, dict):
			for key in ("final_output", "raw", "output"):
				if key in result and result[key]:
					return str(result[key])

		return str(result)

	def _polish_output(
		self,
		label: str,
		content: str,
		*,
		allowed_filenames: Optional[List[str]] = None,
	) -> str:
		"""Rewrite agent output into clear, structured, and actionable guidance."""

		if not content or not content.strip():
			return (
				"**General**\n"
				"Line ?: No findings were reported. Fix: No action required."
			)

		trimmed = content.strip()
		if len(trimmed) > 6000:
			trimmed = textwrap.shorten(trimmed, width=6000, placeholder="... [content truncated]")

		allowed_filenames = allowed_filenames or []
		normalized_allowed = sorted(dict.fromkeys(allowed_filenames))
		allowed_list_text = ""
		if normalized_allowed:
			allowed_list_text = (
				"Allowed class/file names (copy exactly, including extensions): "
				+ ", ".join(normalized_allowed)
				+ "\n"
			)

		prompt = (
			"You are preparing reviewer notes for a pull request. Rewrite the following "
			f"{label.lower()} findings so that each class or file has its own section. "
			"Follow these formatting rules exactly:\n"
			f"{allowed_list_text}"
			"1. For every class or file, output a Markdown bold header on its own line with the exact name (including extension) taken from the original notes. If the notes omit an extension, assume `.py` and append it. Never invent `.java` unless it appears in the original notes.\n"
			"2. Under each header, list each comment on its own line in the format `Line <number>: <issue sentence>. Fix: <clear fix sentence>.`.\n"
			"3. Use simple, easy-to-understand English and reference relevant coding or security standards when helpful.\n"
			"4. If either the class/file name or the line number is missing, write `Unknown` in that position.\n"
			"5. Leave a single blank line between different class or file sections.\n"
			"6. Do not add any other headings, bullet points, numbering, or paragraphs.\n"
			"7. Keep the entire response under 250 words.\n"
			"8. If there are no findings, output exactly `**General**` followed by `Line ?: No findings were reported. Fix: No action required.`\n\n"
			"Original notes:\n"
			f"{trimmed}"
		)

		try:
			if hasattr(self.llm, "invoke"):
				response = self.llm.invoke(prompt)
				if isinstance(response, str):
					polished_text = response
				else:
					polished_text = getattr(response, "content", str(response))
			elif hasattr(self.llm, "predict"):
				polished_text = self.llm.predict(prompt)
			else:
				return trimmed
		except Exception:  # pragma: no cover - defensive fallback
			return trimmed

		polished_text = (polished_text or "").strip()
		if not polished_text:
			return trimmed

		if normalized_allowed:
			allowed_set = {name for name in normalized_allowed}
			allowed_lower_map = {name.lower(): name for name in normalized_allowed}
			allowed_base_map = {Path(name).stem.lower(): name for name in normalized_allowed}
			adjusted_lines: List[str] = []
			for line in polished_text.splitlines():
				stripped = line.strip()
				if stripped.startswith("**") and stripped.endswith("**"):
					inner = stripped.strip("*")
					normalized_inner = inner.strip()
					lower_inner = normalized_inner.lower()
					replacement = None
					if normalized_inner in allowed_set:
						replacement = normalized_inner
					elif lower_inner in allowed_lower_map:
						replacement = allowed_lower_map[lower_inner]
					elif normalized_inner not in {label or "", "General"}:
						candidate_base = Path(normalized_inner).stem.lower()
						if candidate_base in allowed_base_map:
							replacement = allowed_base_map[candidate_base]
					if replacement:
						line = f"**{replacement}**"
				adjusted_lines.append(line)
			polished_text = "\n".join(adjusted_lines)

		return polished_text
