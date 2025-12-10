"""FastAPI application serving the local UI frontend and multi-agent review API."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ..infrastructure.exceptions import AuthenticationError, GitHubClientError, RateLimitError
from ..infrastructure.github.client import GitHubClient
from ..infrastructure.llm.gemini_provider import GeminiProvider
from ..orchestration.orchestrator import ReviewOrchestrator, create_crewai_llm

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
UI_DIR = PROJECT_ROOT / "ui"
HOME_PAGE = UI_DIR / "home.html"
HOME_CSS = UI_DIR / "home.css"
HOME_JS = UI_DIR / "home.js"

app = FastAPI(
    title="AI Code Review Frontend",
    description="Serves the local HTML interface and API for running AI-powered PR reviews.",
    version="0.2.0",
)


class ReviewRequest(BaseModel):
    """Input payload for triggering a multi-agent code review."""

    github_token: str = Field(..., min_length=1, description="GitHub Personal Access Token")
    gemini_api_key: str = Field(..., min_length=1, description="Google Gemini API key")
    repo_owner: str = Field(..., min_length=1, description="Repository owner or organization")
    repo_name: str = Field(..., min_length=1, description="Repository name")
    pr_number: int = Field(..., gt=0, description="Pull request number")
    gemini_model: Optional[str] = Field(None, description="Gemini model identifier")
    max_files: Optional[int] = Field(None, gt=0, description="Maximum number of files to review")
    max_diff_chars: Optional[int] = Field(
        None,
        gt=200,
        description="Maximum characters from each diff to send to the LLM",
    )


def _truncate_diffs(pull_request, max_diff_chars: Optional[int]) -> None:
    """Trim diff patches to avoid exceeding language-model context limits."""

    if not max_diff_chars or max_diff_chars <= 0:
        return

    suffix = "\n... [TRUNCATED FOR REVIEW] ..."
    for change in pull_request.changes:
        patch = getattr(change, "patch", None)
        if patch and len(patch) > max_diff_chars:
            change.patch = patch[:max_diff_chars] + suffix


@app.get("/", include_in_schema=False)
async def read_home() -> FileResponse:
    """Return the single-page frontend application."""
    if not HOME_PAGE.exists():
        raise HTTPException(status_code=500, detail="UI home.html file not found")
    return FileResponse(HOME_PAGE)


@app.get("/home.css", include_in_schema=False)
async def read_home_css() -> FileResponse:
    """Serve the extracted stylesheet for the frontend."""
    if not HOME_CSS.exists():
        raise HTTPException(status_code=500, detail="UI home.css file not found")
    return FileResponse(HOME_CSS, media_type="text/css")


@app.get("/home.js", include_in_schema=False)
async def read_home_js() -> FileResponse:
    """Serve the extracted JavaScript bundle for the frontend."""
    if not HOME_JS.exists():
        raise HTTPException(status_code=500, detail="UI home.js file not found")
    return FileResponse(HOME_JS, media_type="application/javascript")


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.post("/api/review")
async def run_multi_agent_review(request: ReviewRequest) -> dict:
    """Execute the CrewAI-powered multi-agent review workflow for a pull request."""

    repository = f"{request.repo_owner}/{request.repo_name}"

    try:
        github_client = GitHubClient(request.github_token)
    except AuthenticationError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    except GitHubClientError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Failed to initialize GitHub client: {error}") from error

    try:
        pull_request = github_client.get_pull_request(repository, request.pr_number, include_files=True)
    except RateLimitError as error:
        raise HTTPException(status_code=429, detail=str(error)) from error
    except GitHubClientError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Failed to fetch pull request: {error}") from error

    _truncate_diffs(pull_request, request.max_diff_chars)

    normalized_model = GeminiProvider._normalize_model_name(request.gemini_model)  # pylint: disable=protected-access

    llm_config = {
        "provider": "gemini",
        "model": normalized_model,
        "api_key": request.gemini_api_key,
    }

    try:
        crew_llm = create_crewai_llm(llm_config, temperature=0.15)
    except Exception as error:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=f"Failed to initialize Gemini model: {error}") from error

    try:
        orchestrator = ReviewOrchestrator(crew_llm, verbose=False)
        review_result = orchestrator.run_review(
            pull_request,
            max_files=request.max_files,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Failed to run review workflow: {error}") from error

    return review_result
