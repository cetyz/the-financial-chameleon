# GIT_INSTRUCTIONS.md

This file provides guidance for Git operations and authentication in this repository.

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