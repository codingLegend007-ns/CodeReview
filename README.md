# AI-Powered Code Review Agent

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

**Professional-grade AI code review agent powered by CrewAI, Google Gemini, and Grok**

Automatically analyze GitHub Pull Requests, identify code issues, security vulnerabilities, and suggest actionable improvements.

</div>

---

## 🌟 Features

- **🤖 Multi-Agent Architecture**: Specialized AI agents for different review aspects
  - Code Quality Analyzer
  - Security Vulnerability Scanner
  - Performance Bottleneck Detector
  - Suggestion Generator

- **🧠 Multiple LLM Support**: Seamlessly switch between AI models
  - Google Gemini (Primary)
  - Grok (Secondary)

- **🔍 Comprehensive Analysis**:
  - Code quality and best practices
  - Security vulnerabilities
  - Performance issues
  - SOLID principles violations
  - Design pattern suggestions

- **⚡ High Performance**:
  - Parallel processing of files
  - Smart caching system
  - Rate limit handling
  - Async operations

- **🏗️ Enterprise-Grade Architecture**:
  - SOLID principles
  - Design patterns (Strategy, Factory, Repository, etc.)
  - Clear separation of concerns
  - Extensive error handling

## 📋 Prerequisites

- Python 3.10 or higher
- GitHub Personal Access Token
- Google Gemini API Key
- Git installed

## 🚀 Quick Start

### 1. Clone the Repository

```powershell
git clone <your-repo-url>
cd CrewAI
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file and fill in your credentials:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required
GITHUB_TOKEN=ghp_your_github_token_here
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional
GROK_API_KEY=your_grok_api_key_here
DEFAULT_LLM_PROVIDER=gemini
```

#### Getting API Keys:

**GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `read:user`
4. Copy the token

**Google Gemini API Key:**
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### 5. Install in Development Mode

```powershell
pip install -e .
```

### 6. Run Your First Review

```powershell
# Review a specific pull request
python -m src.cli.main review --repo owner/repository --pr 123

# Or if installed:
code-review review --repo owner/repository --pr 123
```

## 📖 Usage Examples

### Basic Review

```powershell
# Review a PR with default settings
code-review review --repo microsoft/vscode --pr 12345
```

### Advanced Options

```powershell
# Review with specific LLM provider
code-review review --repo microsoft/vscode --pr 12345 --provider gemini

# Verbose output
code-review review --repo microsoft/vscode --pr 12345 --verbose

# Export results to JSON
code-review review --repo microsoft/vscode --pr 12345 --format json --output report.json
```

### List PRs

```powershell
# List open pull requests
code-review list-prs --repo microsoft/vscode --state open --limit 10
```

### Configuration Check

```powershell
# Verify configuration
code-review config --check
```

## 🏗️ Architecture

### Project Structure

```
CrewAI/
├── src/
│   ├── core/                    # Domain logic (entities, interfaces, value objects)
│   ├── infrastructure/          # External integrations (GitHub, LLM, config)
│   ├── agents/                  # CrewAI agents
│   ├── tasks/                   # CrewAI tasks
│   ├── orchestration/           # Workflow orchestration
│   ├── services/                # Application services
│   └── cli/                     # Command-line interface
├── config/                      # Configuration files
├── tests/                       # Test suite
├── docs/                        # Documentation
└── examples/                    # Usage examples
```

### Design Principles

- **SOLID Principles**: Single responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Design Patterns**: Strategy, Factory, Repository, Adapter, Observer, Template Method
- **Clean Architecture**: Clear separation between domain, application, and infrastructure layers

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## 🛠️ Development

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_github.py
```

### Code Quality

```powershell
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

### Adding a New Agent

1. Create agent file in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement required methods
4. Register in orchestrator

Example:

```python
from src.agents.base_agent import BaseAgent
from crewai import Agent

class MyCustomAgent(BaseAgent):
    def create_agent(self) -> Agent:
        return Agent(
            role="Custom Analyzer",
            goal="Analyze specific aspects",
            backstory="Expert in custom analysis",
            llm=self.llm,
            verbose=self.verbose
        )
```

## 📊 Review Output

The tool generates comprehensive reports including:

- **Summary**: Overall code quality assessment
- **Issues by Severity**: Critical, High, Medium, Low, Info
- **Issues by Category**: Security, Performance, Quality, Style
- **Issues by File**: Grouped by affected files
- **Recommendations**: Actionable improvement suggestions
- **Statistics**: Files reviewed, issues found, duration

### Example Output

```
╔═══════════════════════════════════════════════════════════════╗
║         Code Review Report - PR #12345                        ║
╚═══════════════════════════════════════════════════════════════╝

📊 Summary:
  • Status: ✅ Completed
  • Files Reviewed: 15
  • Total Issues: 23
  • Duration: 45.2 seconds

🔴 Issues by Severity:
  • 🔴 2 Critical
  • 🟠 5 High
  • 🟡 8 Medium
  • 🟢 6 Low
  • 🔵 2 Info

📁 Issues by File:
  • src/api/auth.py: 5 issues
  • src/models/user.py: 3 issues
  ...

💡 Top Recommendations:
  1. Fix SQL injection vulnerability in auth module
  2. Add input validation for user data
  3. Implement rate limiting on API endpoints
```

## ⚙️ Configuration

All settings can be configured via environment variables or `.env` file:

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | *required* | GitHub personal access token |
| `GOOGLE_API_KEY` | *required* | Google Gemini API key |
| `DEFAULT_LLM_PROVIDER` | `gemini` | Default LLM provider (gemini/grok) |
| `LOG_LEVEL` | `INFO` | Logging level |

### Review Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILES_PER_REVIEW` | `50` | Maximum files to review per PR |
| `MAX_FILE_SIZE_KB` | `500` | Maximum file size to review (KB) |
| `PARALLEL_PROCESSING` | `true` | Enable parallel processing |
| `MAX_WORKERS` | `4` | Number of parallel workers |
| `TIMEOUT_SECONDS` | `300` | Operation timeout |

See [.env.example](.env.example) for complete list.

## 🔒 Security Best Practices

- **Never commit `.env` file** with real credentials
- Store API keys in environment variables or secure vault
- Use GitHub tokens with minimal required scopes
- Enable SSL validation in production
- Regularly rotate API keys
- Review logs for sensitive data leakage

## 🐛 Troubleshooting

### Common Issues

**1. GitHub Rate Limit Exceeded**
```
Error: GitHub API rate limit exceeded
```
**Solution**: Wait for rate limit reset or use authenticated requests with higher limits.

**2. Invalid API Key**
```
Error: Authentication failed
```
**Solution**: Verify your API keys in `.env` file are correct and active.

**3. Import Errors**
```
ModuleNotFoundError: No module named 'src'
```
**Solution**: Install in development mode: `pip install -e .`

**4. Connection Timeout**
```
Error: Request timeout
```
**Solution**: Increase `TIMEOUT_SECONDS` in settings or check network connection.

## 📚 Documentation

- [Architecture Overview](ARCHITECTURE.md) - System architecture and design
- [API Documentation](docs/api.md) - API reference (coming soon)
- [Development Guide](docs/development.md) - Contributing guidelines (coming soon)
- [Deployment Guide](docs/deployment.md) - Production deployment (coming soon)

## 🗺️ Roadmap

### Phase 1: Core Features (Week 1) ✅
- [x] Project setup and architecture
- [x] Core domain models
- [x] GitHub integration
- [x] LLM provider abstractions
- [x] Basic agents and tasks
- [x] CLI interface

### Phase 2: Enhanced Features (Week 2)
- [ ] Advanced security analysis
- [ ] Performance profiling
- [ ] Custom rule engine
- [ ] GitHub PR comments
- [ ] Webhook integration

### Phase 3: Enterprise Features (Future)
- [ ] Web dashboard
- [ ] Team collaboration
- [ ] Custom agent creation
- [ ] Historical analytics
- [ ] CI/CD integration

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guide
- All tests pass
- New features have tests
- Documentation is updated

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) - LLM provider
- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API wrapper

## 📧 Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Email: your.email@example.com

---

<div align="center">

**Built with ❤️ using CrewAI and Google Gemini**

[Report Bug](issues) · [Request Feature](issues) · [Documentation](docs/)

</div>
