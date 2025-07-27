# DEVELOPMENT_INSTRUCTIONS.md

This file provides guidance for local development workflow in this repository.

## Environment Setup

```bash
cd daily-check
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running Locally

```bash
cd daily-check
python main.py
```

## Testing Cloud Function

The main function expects a request parameter but can be tested locally by modifying the main block.