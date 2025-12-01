# Getting Started Guide

This guide will walk you through setting up and running the AI Code Review Agent from scratch in under 15 minutes.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Windows 10/11 with PowerShell
- [ ] Python 3.10 or higher installed
- [ ] Git installed
- [ ] GitHub account
- [ ] Google account (for Gemini API)
- [ ] Internet connection

## 🚀 Step-by-Step Setup

### Step 1: Verify Python Installation

Open PowerShell and verify Python version:

```powershell
python --version
```

Should output: `Python 3.10.x` or higher

If not installed, download from: https://www.python.org/downloads/

### Step 2: Navigate to Project Directory

```powershell
cd d:\Development\AI\CrewAI
```

### Step 3: Create and Activate Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Note**: If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Your prompt should now show `(venv)` at the beginning.

### Step 4: Upgrade pip and Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This will take 2-3 minutes. Wait for all packages to install.

### Step 5: Get Your API Keys

#### GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: "Code Review Agent"
4. Select expiration: 90 days (or your preference)
5. Select scopes:
   - ✅ `repo` (all)
   - ✅ `read:org`
   - ✅ `read:user`
6. Click **"Generate token"**
7. **COPY THE TOKEN** (you won't see it again!)

#### Google Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click **"Create API Key"**
3. Select existing Google Cloud project or create new one
4. **COPY THE API KEY**

### Step 6: Configure Environment Variables

```powershell
# Copy example environment file
Copy-Item .env.example .env

# Open .env file in notepad
notepad .env
```

Edit the `.env` file and add your API keys:

```env
# Required - Paste your actual tokens here
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional - Leave defaults
GEMINI_MODEL=gemini-1.5-pro-latest
DEFAULT_LLM_PROVIDER=gemini
LOG_LEVEL=INFO
```

**Save and close** the file.

### Step 7: Install Package in Development Mode

```powershell
pip install -e .
```

### Step 8: Verify Installation

```powershell
# Check configuration
python -m src.cli.main config --check
```

You should see:
```
✅ GitHub: Connected
   Rate limit: 5000/5000
✅ LLM (gemini): Connected

Configuration check complete!
```

### Step 9: Run Your First Code Review

Let's review a real pull request from a public repository:

```powershell
# Review a Microsoft VS Code pull request (example)
python -m src.cli.main review --repo microsoft/vscode --pr 2f5aca --verbose
```

Replace `201234` with any actual PR number from the repository.

Or use a smaller repository for testing:

```powershell
# Review a pull request from your own repository
python -m src.cli.main review --repo yourusername/yourrepo --pr 1
```

### Step 10: Explore Features

#### List Pull Requests

```powershell
# List open PRs in a repository
python -m src.cli.main list-prs --repo microsoft/vscode --state open --limit 5
```

#### Review with Different Options

```powershell
# Verbose output
python -m src.cli.main review --repo owner/repo --pr 123 --verbose

# Use Grok (if configured)
python -m src.cli.main review --repo owner/repo --pr 123 --provider grok
```

## 🎯 Quick Test Workflow

Here's a complete test workflow using a public repository:

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Check configuration
python -m src.cli.main config --check

# 3. List recent PRs to find one to review
python -m src.cli.main list-prs --repo torvalds/linux --state closed --limit 3

# 4. Review a specific PR
python -m src.cli.main review --repo torvalds/linux --pr [PR_NUMBER] --verbose
```

## 📊 Understanding the Output

When you run a review, you'll see:

1. **Configuration Loading**: Validates your setup
2. **GitHub Connection**: Connects and fetches PR data
3. **PR Summary**: Shows PR details, files, and changes
4. **LLM Initialization**: Connects to Google Gemini
5. **Code Analysis**: Reviews each changed file
6. **Results**: Displays findings and suggestions

Example output:

```
🤖 AI Code Review Agent
============================================================
✓ Configuration loaded
  Repository: microsoft/vscode
  PR Number: #123
  LLM Provider: gemini

✓ Connected to GitHub

✓ Fetched PR: Fix memory leak in extension host
  Author: user123
  Files changed: 3
  Changes: +45/-12

🔍 Performing basic code review...

📄 src/vs/workbench/api/common/extHost.ts

Analysis:
1. Memory Management: The added code properly handles cleanup...
2. Error Handling: Missing try-catch block around line 45...
3. Performance: Consider caching the result of...

✅ Review Complete!
```

## 🔧 Troubleshooting

### Issue: "Import errors" or "Module not found"

**Solution**:
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "GitHub API rate limit exceeded"

**Solution**: 
- Wait for rate limit reset (check with `config --check`)
- Authenticated requests have 5000/hour limit vs 60/hour unauthenticated

### Issue: "Invalid GitHub token"

**Solution**:
1. Verify token in `.env` file
2. Ensure token has correct scopes (`repo`, `read:org`)
3. Generate new token if expired

### Issue: "Gemini API error"

**Solution**:
1. Verify API key in `.env` file
2. Check API key is active at https://makersuite.google.com/app/apikey
3. Ensure you have Gemini API access enabled

### Issue: "PowerShell execution policy error"

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: SSL Certificate Verification Failed

**Solution**: Add to `.env`:
```env
VALIDATE_SSL=false
```
(Not recommended for production)

## 🎓 Next Steps

Now that you have the basic setup running:

1. **Explore the Code**: Review `src/` directory structure
2. **Add Custom Agents**: Create specialized review agents
3. **Integrate CrewAI**: Implement full multi-agent workflow
4. **Customize Prompts**: Modify analysis prompts in `config/prompts/`
5. **Add Tests**: Write tests in `tests/` directory

## 📚 Additional Resources

- **Architecture Documentation**: See [ARCHITECTURE.md](../ARCHITECTURE.md)
- **README**: See [README.md](../README.md)
- **API Keys**: 
  - GitHub: https://github.com/settings/tokens
  - Google Gemini: https://makersuite.google.com/app/apikey

## ⏱️ Development Timeline

### Week 1 - Days 1-2: Foundation ✅
- [x] Project structure
- [x] Core domain models
- [x] GitHub integration
- [x] LLM providers
- [x] Basic CLI

### Week 1 - Days 3-4: CrewAI Integration (Next Steps)
- [ ] Implement CrewAI agents
- [ ] Define agent tasks
- [ ] Create orchestration layer
- [ ] Prompt engineering

### Week 1 - Days 5-6: Features & Polish
- [ ] Advanced analysis
- [ ] Report generation
- [ ] Error handling
- [ ] Logging system

### Week 1 - Day 7: Testing & Documentation
- [ ] Unit tests
- [ ] Integration tests
- [ ] Example scripts
- [ ] Documentation completion

## 🎉 Success Criteria

You're ready to proceed to development if:

- [x] Virtual environment activated
- [x] All dependencies installed without errors
- [x] Configuration check passes
- [x] Successfully reviewed at least one PR
- [x] Understood basic CLI commands

## 💡 Pro Tips

1. **Use VSCode**: Open project in VS Code for better development experience
2. **Enable Git**: Initialize git repository for version control
3. **Create Branch**: Work on feature branches for experimentation
4. **Test Incrementally**: Test each component as you build
5. **Read Logs**: Check console output for debugging information

## 🚀 Ready to Build!

You now have a fully functional foundation. The next steps are:

1. Implement CrewAI agents (see `src/agents/`)
2. Define specialized tasks (see `src/tasks/`)
3. Create orchestration workflow (see `src/orchestration/`)
4. Enhance with advanced features

Happy coding! 🎉
