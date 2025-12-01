# QuickStart Script for AI Code Review Agent
# This script helps you get started quickly

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Code Review Agent - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(1[0-9]|[2-9][0-9])") {
    Write-Host "✓ Python version OK: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3.10+ required. Current: $pythonVersion" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($?) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

if ($?) {
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ Pip upgraded" -ForegroundColor Green

Write-Host ""

# Install dependencies
Write-Host "Installing dependencies (this may take 2-3 minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($?) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check for .env file
if (Test-Path ".env") {
    Write-Host "✓ Configuration file (.env) exists" -ForegroundColor Green
} else {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env file and add your API keys:" -ForegroundColor Red
    Write-Host "   1. GitHub Token: https://github.com/settings/tokens" -ForegroundColor Yellow
    Write-Host "   2. Google Gemini API Key: https://makersuite.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to open .env file in notepad..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    notepad .env
}

Write-Host ""

# Install package in development mode
Write-Host "Installing package in development mode..." -ForegroundColor Yellow
pip install -e . --quiet
if ($?) {
    Write-Host "✓ Package installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install package" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! 🎉" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify configuration:" -ForegroundColor White
Write-Host "   python -m src.cli.main config --check" -ForegroundColor Gray
Write-Host ""
Write-Host "2. List pull requests:" -ForegroundColor White
Write-Host "   python -m src.cli.main list-prs --repo microsoft/vscode --limit 5" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Review a pull request:" -ForegroundColor White
Write-Host "   python -m src.cli.main review --repo owner/repo --pr 123 --verbose" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed guide, see: GETTING_STARTED.md" -ForegroundColor Cyan
Write-Host ""
