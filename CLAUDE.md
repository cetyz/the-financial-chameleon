# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Financial Chameleon is a financial analysis tool that provides investment recommendations through Telegram bots. The system analyzes stock market data (primarily VOO ETF) using moving averages, sentiment indicators, and the Fear & Greed Index to generate investment advice.

## Architecture

### Core Components

- **daily-check/**: Google Cloud Function that runs daily market analysis
  - `main.py`: Main Cloud Function entry point with market analysis logic
  - `requirements.txt`: Python dependencies for the cloud function
  - `venv/`: Virtual environment (not committed to version control)

- **legacy-code/**: Contains previous implementation (`legacy.py`) with similar functionality but different structure

### Key Functions & Data Flow

1. **Data Collection**: `get_ticker_data()` fetches stock data using yfinance
2. **Processing**: `process_data()` calculates moving averages (50MA, 100MA, 200MA)
3. **Sentiment Analysis**: `get_bull_bear()` determines market trend, `get_fng()` gets Fear & Greed Index
4. **Decision Logic**: `get_siit()` uses decision tables to generate investment recommendations
5. **Communication**: Telegram bot integration sends messages to specified channels

### Decision Matrix

The system uses bull/bear decision tables that cross-reference:
- Current price relative to moving averages (50MA+-, 50MA, 100MA, 200MA zones)
- Fear & Greed Index sentiment (extreme fear, fear, neutral, greed, extreme greed)

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
**NOT**:
```
GITHUB_TOKEN = "your_token_here"
```

### Git Authentication Setup
```bash
# CORRECT: Use source to load .env variables
source .env

# ALTERNATIVE: Extract token manually (if source doesn't work)
export GITHUB_TOKEN="$(grep GITHUB_TOKEN .env | cut -d'=' -f2 | tr -d '"')"

# For push operations, use:
git push https://$GITHUB_TOKEN@github.com/cetyz/the-financial-chameleon.git main

# For clone operations (if needed):
git clone https://$GITHUB_TOKEN@github.com/cetyz/the-financial-chameleon.git
```

### Standard Git Workflow
1. Make changes to files
2. Stage changes: `git add .` (but **NEVER** stage .env file)
3. Commit with proper message format
4. **Load environment**: `source .env`
5. Push: `git push https://$GITHUB_TOKEN@github.com/cetyz/the-financial-chameleon.git main`

### Important Security Notes
- **NEVER commit the .env file** - it contains private authentication tokens
- The .env file should be in .gitignore to prevent accidental commits
- Always use `source .env` as the primary method to load environment variables
- If `source .env` fails, use the manual export method as fallback

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

## Code Structure Notes

- The refactored `daily-check/main.py` has improved modularity with proper type hints and docstrings
- Legacy code in `legacy-code/` contains similar logic but in a single monolithic structure
- Decision tables are hardcoded with emoji-rich investment advice messages
- The system currently focuses on VOO (Vanguard S&P 500 ETF) analysis