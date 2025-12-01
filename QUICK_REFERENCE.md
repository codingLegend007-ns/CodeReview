# Quick Reference Card

## 🚀 Essential Commands

### Setup
```powershell
.\quickstart.ps1                                    # Automated setup
python -m src.cli.main config --check              # Verify configuration
```

### Review Operations
```powershell
# Review a PR
python -m src.cli.main review --repo owner/repo --pr 123

# Review with verbose output
python -m src.cli.main review --repo owner/repo --pr 123 --verbose

# Review with specific provider
python -m src.cli.main review --repo owner/repo --pr 123 --provider gemini
```

### List Operations
```powershell
# List open PRs
python -m src.cli.main list-prs --repo owner/repo

# List closed PRs
python -m src.cli.main list-prs --repo owner/repo --state closed --limit 10
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/cli/main.py` | CLI entry point |
| `src/core/entities/` | Domain models |
| `src/infrastructure/github/client.py` | GitHub client |
| `src/infrastructure/llm/gemini_provider.py` | LLM provider |
| `src/infrastructure/config/settings.py` | Configuration |
| `.env` | API keys and settings |

## 🔑 Environment Variables

```env
GITHUB_TOKEN=ghp_xxx                    # Required
GOOGLE_API_KEY=AIzaSyxxx               # Required
DEFAULT_LLM_PROVIDER=gemini            # gemini or grok
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING, ERROR
MAX_WORKERS=4                           # Parallel processing threads
```

## 🏗️ Project Structure

```
src/
├── core/           # Domain logic
├── infrastructure/ # External systems
├── agents/         # CrewAI agents
├── tasks/          # Agent tasks
├── orchestration/  # Workflow (TODO)
├── services/       # Application services (TODO)
└── cli/            # Command-line interface
```

## 🎯 Next Implementation Steps

1. Create `src/orchestration/orchestrator.py`
2. Create `config/prompts/*.txt` prompt templates
3. Create `src/services/report_service.py`
4. Update CLI to use orchestrator
5. Add logging system
6. Write tests

## 🔍 Debugging

```powershell
# Enable verbose mode
--verbose

# Check logs
LOG_LEVEL=DEBUG in .env

# Python debugging
import pdb; pdb.set_trace()
```

## 🧪 Testing (TODO)

```powershell
pytest                              # Run all tests
pytest tests/unit/                  # Run unit tests
pytest tests/integration/           # Run integration tests
pytest --cov=src                    # With coverage
```

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| README.md | Overview & quick start |
| GETTING_STARTED.md | Detailed setup |
| ARCHITECTURE.md | System design |
| ROADMAP.md | Implementation plan |
| BEST_PRACTICES.md | Coding standards |
| PROJECT_SUMMARY.md | Status & progress |

## 🆘 Quick Fixes

**Import errors?**
```powershell
pip install -e .
```

**Authentication failed?**
```powershell
notepad .env  # Check API keys
python -m src.cli.main config --check
```

**Rate limit exceeded?**
```powershell
python -m src.cli.main config --check  # Check remaining
# Wait or use different token
```

**Module not found?**
```powershell
.\venv\Scripts\Activate.ps1  # Activate venv
pip install -r requirements.txt
```

## 💡 Tips

- Use `--verbose` for debugging
- Test with small PRs first
- Check rate limits regularly
- Read inline code documentation
- Commit changes frequently
- Follow SOLID principles

## 🎓 Learning

- CrewAI: https://docs.crewai.com/
- Gemini: https://ai.google.dev/docs
- PyGithub: https://pygithub.readthedocs.io/
- Python Type Hints: https://docs.python.org/3/library/typing.html

## 📊 Status

- ✅ Foundation: Complete (75%)
- ⏳ CrewAI Integration: In Progress (20%)
- ⏳ Advanced Features: Pending
- ⏳ Testing: Pending

---

**Print this for quick reference!**
