"""Command-line interface for code review agent."""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..infrastructure.config.settings import get_settings
from ..infrastructure.github.client import GitHubClient
from ..infrastructure.llm.factory import LLMProviderFactory
from ..infrastructure.exceptions import CodeReviewError

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def app():
    """AI-Powered Code Review Agent using CrewAI and Google Gemini."""
    pass


@app.command()
@click.option("--repo", required=True, help="Repository in format owner/repo")
@click.option("--pr", required=True, type=int, help="Pull request number")
@click.option("--provider", help="LLM provider (gemini/grok)")
@click.option("--verbose", is_flag=True, help="Verbose output")
@click.option("--format", "output_format", default="markdown", help="Output format")
@click.option("--output", help="Output file path")
def review(repo: str, pr: int, provider: str, verbose: bool, output_format: str, output: str):
    """Review a GitHub pull request."""
    try:
        console.print("\n[bold blue]🤖 AI Code Review Agent[/bold blue]")
        console.print("=" * 60)
        
        # Load settings
        with console.status("[bold green]Loading configuration..."):
            settings = get_settings()
            if provider:
                settings.default_llm_provider = provider
        
        console.print(f"✓ Configuration loaded")
        console.print(f"  Repository: {repo}")
        console.print(f"  PR Number: #{pr}")
        console.print(f"  LLM Provider: {settings.default_llm_provider}\n")
        
        # Initialize GitHub client
        with console.status("[bold green]Connecting to GitHub..."):
            github_client = GitHubClient(settings.github_token)
            github_client.validate_connection()
        
        console.print("✓ Connected to GitHub\n")
        
        # Fetch pull request
        with console.status(f"[bold green]Fetching PR #{pr}..."):
            pull_request = github_client.get_pull_request(repo, pr, include_files=True)
        
        console.print(f"✓ Fetched PR: {pull_request.title}")
        console.print(f"  Author: {pull_request.author}")
        console.print(f"  Files changed: {pull_request.changed_files_count}")
        console.print(f"  Changes: +{pull_request.total_additions}/-{pull_request.total_deletions}\n")
        
        # Display files
        if verbose:
            console.print("[bold]Changed Files:[/bold]")
            for change in pull_request.significant_changes[:10]:
                console.print(f"  • {change.filename} ({change.status.value})")
            if len(pull_request.significant_changes) > 10:
                console.print(f"  ... and {len(pull_request.significant_changes) - 10} more\n")
        
        # Initialize LLM
        with console.status("[bold green]Initializing LLM provider..."):
            llm_config = settings.get_llm_config()
            llm_provider = LLMProviderFactory.create(
                llm_config["provider"],
                llm_config["api_key"],
                llm_config["model"]
            )
        
        console.print(f"✓ LLM initialized: {llm_provider}\n")
        
        # Simple review demo (without CrewAI agents for now)
        console.print("[bold yellow]🔍 Performing basic code review...[/bold yellow]\n")
        
        issues_found = []
        
        for change in pull_request.significant_changes[:5]:  # Limit for demo
            with console.status(f"[green]Analyzing {change.filename}..."):
                if change.patch and len(change.patch) < 2000:
                    # Create simple review prompt
                    prompt = f"""Review the following code change and identify potential issues:

File: {change.filename}
Language: {change.language or 'unknown'}

Changes:
{change.patch[:1500]}

Please identify:
1. Code quality issues
2. Potential bugs
3. Security concerns
4. Performance issues
5. Best practice violations

Provide a concise analysis."""
                    
                    try:
                        analysis = llm_provider.generate(prompt, temperature=0.3, max_tokens=500)
                        issues_found.append({
                            "file": change.filename,
                            "analysis": analysis
                        })
                    except Exception as e:
                        console.print(f"[red]Error analyzing {change.filename}: {e}[/red]")
        
        # Display results
        console.print("\n[bold green]✅ Review Complete![/bold green]\n")
        
        console.print(Panel.fit(
            f"[bold]Review Summary[/bold]\n\n"
            f"Files Analyzed: {len(issues_found)}\n"
            f"Total Files: {len(pull_request.significant_changes)}",
            border_style="green"
        ))
        
        # Display findings
        for item in issues_found:
            console.print(f"\n[bold cyan]📄 {item['file']}[/bold cyan]")
            console.print(item['analysis'][:500] + "..." if len(item['analysis']) > 500 else item['analysis'])
        
        console.print("\n[bold]💡 Note:[/bold] This is a basic demo. Full agent-based review coming soon!")
        
    except CodeReviewError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {e}", style="red")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@app.command()
@click.option("--repo", required=True, help="Repository in format owner/repo")
@click.option("--state", default="open", help="PR state (open/closed/all)")
@click.option("--limit", default=10, type=int, help="Number of PRs to list")
def list_prs(repo: str, state: str, limit: int):
    """List pull requests in a repository."""
    try:
        settings = get_settings()
        github_client = GitHubClient(settings.github_token)
        
        console.print(f"\n[bold]Fetching {state} pull requests from {repo}...[/bold]\n")
        
        prs = github_client.list_pull_requests(repo, state, limit)
        
        table = Table(title=f"Pull Requests - {repo}")
        table.add_column("PR #", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Author", style="yellow")
        table.add_column("State", style="magenta")
        table.add_column("Files", style="blue")
        
        for pr in prs:
            table.add_row(
                str(pr.number),
                pr.title[:50] + "..." if len(pr.title) > 50 else pr.title,
                pr.author,
                pr.state,
                str(pr.changed_files_count)
            )
        
        console.print(table)
        console.print(f"\nTotal: {len(prs)} pull requests\n")
        
    except CodeReviewError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        sys.exit(1)


@app.command()
@click.option("--check", is_flag=True, help="Check configuration validity")
def config(check: bool):
    """Display or check configuration."""
    try:
        settings = get_settings()
        
        if check:
            console.print("\n[bold]Checking configuration...[/bold]\n")
            
            # Check GitHub
            try:
                github_client = GitHubClient(settings.github_token)
                github_client.validate_connection()
                console.print("✅ GitHub: Connected")
                
                rate_limit = github_client.get_rate_limit()
                console.print(f"   Rate limit: {rate_limit['core']['remaining']}/{rate_limit['core']['limit']}")
            except Exception as e:
                console.print(f"❌ GitHub: Failed - {e}")
            
            # Check LLM
            try:
                llm_config = settings.get_llm_config()
                llm_provider = LLMProviderFactory.create(
                    llm_config["provider"],
                    llm_config["api_key"],
                    llm_config["model"]
                )
                llm_provider.validate_connection()
                console.print(f"✅ LLM ({llm_config['provider']}): Connected")
            except Exception as e:
                console.print(f"❌ LLM: Failed - {e}")
            
            console.print("\n[bold green]Configuration check complete![/bold green]\n")
        else:
            console.print("\n[bold]Current Configuration:[/bold]\n")
            console.print(f"GitHub API: {settings.github_api_url}")
            console.print(f"LLM Provider: {settings.default_llm_provider}")
            console.print(f"Log Level: {settings.log_level}")
            console.print(f"Max Workers: {settings.max_workers}")
            console.print(f"Parallel Processing: {settings.parallel_processing}")
            console.print()
            
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    app()
