# API Keys Setup Guide

## Overview

This guide walks you through obtaining all necessary API keys for the AI Code Review Agent.

## 🔑 Required API Keys

### 1. GitHub Personal Access Token

**Purpose**: Access GitHub repositories and pull requests

**Steps**:

1. **Go to GitHub Settings**
   - Navigate to: https://github.com/settings/tokens
   - Or: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token**
   - Click **"Generate new token"** dropdown
   - Select **"Generate new token (classic)"**

3. **Configure Token**
   - **Note**: Enter a descriptive name (e.g., "AI Code Review Agent")
   - **Expiration**: Select 90 days or your preference
   
4. **Select Scopes** (Check these boxes):
   - ✅ **repo** (all checkboxes under it)
     - repo:status
     - repo_deployment
     - public_repo
     - repo:invite
     - security_events
   - ✅ **read:org**
   - ✅ **read:user**
   - ✅ **user:email**

5. **Generate Token**
   - Click **"Generate token"** at the bottom
   - **IMPORTANT**: Copy the token immediately (starts with `ghp_`)
   - You won't be able to see it again!

6. **Save Token**
   - Paste it in `.env` file:
   ```env
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Token Format**: `ghp_` followed by 36 characters

**Example**: `ghp_1234567890abcdefghijklmnopqrstuvwxyz`

---

### 2. Google Gemini API Key

**Purpose**: Access Google's Gemini AI model for code analysis

**Steps**:

1. **Go to Google AI Studio**
   - Navigate to: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/app/apikey

2. **Sign In**
   - Use your Google account
   - Accept terms if prompted

3. **Create API Key**
   - Click **"Create API Key"** button
   
4. **Select Project**
   - Choose existing Google Cloud project, or
   - Create new project (will be created automatically)

5. **Copy API Key**
   - Key will be displayed (starts with `AIzaSy`)
   - Click copy button
   - **IMPORTANT**: Store it securely

6. **Save API Key**
   - Paste it in `.env` file:
   ```env
   GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Key Format**: `AIzaSy` followed by 33 characters

**Example**: `AIzaSyABcD1234567890eFgHiJkLmNoPqRsTuVwXyZ`

**Notes**:
- Free tier includes 60 requests per minute
- Monitor usage at: https://makersuite.google.com/app/apikey
- Set up billing for higher limits (optional)

---

### 3. Grok API Key (Optional)

**Purpose**: Alternative AI model from X.AI (optional, for testing)

**Status**: Currently in limited beta

**Steps** (when available):

1. **Sign Up for Access**
   - Visit: https://x.ai/api
   - Join waitlist or apply for access

2. **Get API Key**
   - Once approved, access API dashboard
   - Generate API key

3. **Save API Key**
   - Paste it in `.env` file:
   ```env
   GROK_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   GROK_API_URL=https://api.x.ai/v1
   ```

**Note**: Grok is optional. The system works fine with just Gemini.

---

## 🔐 Security Best Practices

### DO ✅
- Store keys in `.env` file (never commit to git)
- Use environment variables
- Rotate keys periodically (every 90 days)
- Use minimal required scopes
- Monitor API usage
- Revoke unused keys

### DON'T ❌
- Hardcode keys in source code
- Commit `.env` file to git
- Share keys via email/chat
- Use the same key across projects
- Leave unused keys active
- Grant unnecessary permissions

## 📝 .env File Template

Create or edit `d:\Development\AI\CrewAI\.env`:

```env
# ================================
# GitHub Configuration
# ================================
# Get token from: https://github.com/settings/tokens
# Required scopes: repo, read:org, read:user
GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_API_URL=https://api.github.com

# ================================
# Google Gemini Configuration
# ================================
# Get API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=AIzaSy_your_actual_key_here
GEMINI_MODEL=gemini-1.5-pro-latest

# ================================
# Grok Configuration (Optional)
# ================================
# Get API key from: https://x.ai/api (when available)
# GROK_API_KEY=xai_your_actual_key_here
# GROK_API_URL=https://api.x.ai/v1
# GROK_MODEL=grok-beta

# ================================
# Default Settings
# ================================
DEFAULT_LLM_PROVIDER=gemini
LOG_LEVEL=INFO
MAX_FILES_PER_REVIEW=50
MAX_FILE_SIZE_KB=500
ENABLE_CACHING=true
CACHE_TTL_HOURS=24

# ================================
# Processing Configuration
# ================================
PARALLEL_PROCESSING=true
MAX_WORKERS=4
TIMEOUT_SECONDS=300

# ================================
# Output Settings
# ================================
OUTPUT_FORMAT=markdown
VERBOSE=false
COLOR_OUTPUT=true

# ================================
# Rate Limiting
# ================================
GITHUB_RATE_LIMIT_PAUSE=60
LLM_RATE_LIMIT_PAUSE=10
MAX_RETRIES=3

# ================================
# Security
# ================================
VALIDATE_SSL=true
MASK_SENSITIVE_DATA=true
```

## ✅ Verify Setup

After adding your API keys, verify they work:

```powershell
# Check configuration
python -m src.cli.main config --check
```

**Expected Output**:
```
Checking configuration...

✅ GitHub: Connected
   Rate limit: 5000/5000
✅ LLM (gemini): Connected

Configuration check complete!
```

## 🔍 Troubleshooting

### GitHub Token Issues

**Error**: "Invalid GitHub token" or "401 Unauthorized"

**Solutions**:
1. Verify token in `.env` starts with `ghp_`
2. Check token hasn't expired
3. Ensure all required scopes are selected
4. Generate new token if needed

**Test Token**:
```powershell
# Using curl (if installed)
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Using PowerShell
$headers = @{Authorization = "token YOUR_TOKEN"}
Invoke-RestMethod -Uri https://api.github.com/user -Headers $headers
```

### Gemini API Issues

**Error**: "Invalid API key" or "403 Forbidden"

**Solutions**:
1. Verify key in `.env` starts with `AIzaSy`
2. Check key is enabled in Google AI Studio
3. Ensure Gemini API is enabled for your project
4. Check rate limits aren't exceeded

**Test Key**:
```powershell
# Using curl (if installed)
curl -H "Content-Type: application/json" -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_KEY"
```

### Rate Limit Issues

**Error**: "API rate limit exceeded"

**Solutions**:
1. Wait for rate limit reset
2. Check current limits: `python -m src.cli.main config --check`
3. For GitHub: Use authenticated requests (higher limit)
4. For Gemini: Wait 1 minute (60 requests/minute)

### Environment Not Loading

**Error**: Keys not being read from `.env`

**Solutions**:
1. Verify `.env` file exists in project root
2. Check file encoding is UTF-8
3. Ensure no spaces around `=` sign
4. Restart terminal/reload environment
5. Try absolute path in code

```powershell
# Verify .env file
Test-Path .env  # Should return True
Get-Content .env  # Should show your configuration
```

## 🔄 Key Rotation

**Recommended**: Rotate keys every 90 days

### GitHub Token Rotation
1. Generate new token (same process)
2. Update `.env` file
3. Test new token
4. Revoke old token

### Gemini Key Rotation
1. Create new API key in AI Studio
2. Update `.env` file
3. Test new key
4. Delete old key

## 📊 API Limits

### GitHub API Limits
- **Authenticated**: 5,000 requests/hour
- **Unauthenticated**: 60 requests/hour
- **Search**: 30 requests/minute

### Google Gemini Limits (Free Tier)
- **Requests**: 60 per minute
- **Tokens**: 32,000 per minute
- **Daily**: 1,500 requests

**Upgrade**: For higher limits, enable billing in Google Cloud

## 🆘 Getting Help

If you encounter issues:

1. ✅ Check this guide
2. ✅ Verify API keys are valid
3. ✅ Run configuration check
4. ✅ Check API provider status pages:
   - GitHub: https://www.githubstatus.com/
   - Google: https://status.cloud.google.com/
5. ✅ Review error messages carefully
6. ✅ Check GETTING_STARTED.md troubleshooting section

## 🎉 Success!

Once configuration check passes, you're ready to use the code review agent!

```powershell
# List some PRs
python -m src.cli.main list-prs --repo microsoft/vscode --limit 5

# Review a PR
python -m src.cli.main review --repo owner/repo --pr 123 --verbose
```

---

**Keep your API keys secure and never share them!** 🔒
