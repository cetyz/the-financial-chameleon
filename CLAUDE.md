# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
cd daily-check
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Locally
```bash
cd daily-check
python main.py
```

### Testing Cloud Function
The main function expects a request parameter but can be tested locally by modifying the main block.

## Git Operations & Authentication

**CRITICAL**: All GitHub operations (commits, pushes, pulls) must use the authentication token stored in `.env` file in the repository root.

### .env File Format Requirements
The `.env` file must follow standard format without spaces around the equals sign:
```
GITHUB_TOKEN="your_token_here"
```

### Git Authentication Setup (One-time setup)
```bash
# Configure Git to use credential helper
git config --local credential.helper store

# Store GitHub credentials (extracts token from .env file)
echo "https://$(grep GITHUB_TOKEN .env | cut -d'=' -f2 | tr -d '\"'):@github.com" > ~/.git-credentials
```

### Standard Git Workflow
1. Make changes to files
2. Stage changes: `git add .` (but **NEVER** stage .env file)
3. Commit with proper message format
4. Push: `git push origin main`

### Important Security Notes
- **NEVER commit the .env file** - it contains private authentication tokens
- The .env file should be in .gitignore to prevent accidental commits
- The credential setup is one-time only - subsequent pushes will work automatically
- If authentication fails, re-run the credential setup commands above

## Key Dependencies

- **yfinance**: Stock market data retrieval
- **pandas/numpy**: Data processing and analysis
- **fear-and-greed**: Market sentiment indicator
- **python-telegram-bot**: Telegram integration
- **google-cloud-***: Google Cloud services (Secret Manager, Storage)

## Configuration

- Telegram bot tokens stored in Google Cloud Secret Manager
- Project ID: "the-financial-chameleon"
- Bot names: 'financial-chameleon', 'trading-chameleon', 'crypto-chameleon'
- Main channel: '@thefinancialchameleon'
- Debug channel: '@testchameleonchannel'

### GCP Service Account
- Service account JSON file: `private/the-financial-chameleon-bf516ef64faa.json`
- **NEVER commit the private folder** - it contains sensitive authentication credentials

