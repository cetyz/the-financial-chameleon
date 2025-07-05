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

### GCP Service Accounts
- **Admin Service Account**: `private/the-financial-chameleon-bf516ef64faa.json`
  - **NEVER commit the private folder** - it contains sensitive authentication credentials
- **Cloud Scheduler Service Account**: `cloud-scheduler-sa@the-financial-chameleon.iam.gserviceaccount.com`
  - Purpose: Cloud Scheduler-invoked Cloud Functions
  - Role: `roles/cloudfunctions.invoker`
  - Description: "Claude-created SA for Cloud Scheduler-invoked Cloud Functions"
- **Daily Check Service Account**: `fin-cham-daily-check-sa@the-financial-chameleon.iam.gserviceaccount.com`
  - Purpose: Daily check Cloud Function runtime execution
  - Role: `roles/secretmanager.secretAccessor`
  - Description: "Claude-created SA that will handle the financial chameleon daily check runtime upon cloud function invocation"
  - Required for: Accessing Telegram bot tokens from Secret Manager during Cloud Function execution

### Google Cloud CLI
- **CRITICAL**: Always use the WSL installation of gcloud, not the Windows installation
- **REQUIRED**: Use the full path `/home/cetyz/google-cloud-sdk/bin/gcloud` for all gcloud commands to avoid conflicts with Windows installation
- Ensure `gcloud` commands are run within the WSL environment to maintain consistency with the project setup

### Bash Tool Timeout Requirements
- **CRITICAL**: Cloud Function deployments require extended timeouts due to build and deployment time (3-5 minutes)
- **REQUIRED**: Always use `--timeout=600000` (10 minutes) parameter when running gcloud functions deploy commands
- Default bash timeout of 2 minutes will always fail for Cloud Function deployments

## Cloud Functions & Scheduler Deployments

### Current Production Deployment
- **Function Name**: `financial-chameleon-daily-check`
- **Region**: `asia-southeast1` (Singapore)
- **Runtime**: Python 3.11, Gen 2
- **Memory**: 1Gi, **Timeout**: 540s
- **Entry Point**: `main` function in `daily-check/main.py`
- **Cloud Run URL**: `https://financial-chameleon-daily-check-nlvd6y7vqa-as.a.run.app`
- **Cloud Functions URL**: `https://asia-southeast1-the-financial-chameleon.cloudfunctions.net/financial-chameleon-daily-check`
- **Runtime Service Account**: `fin-cham-daily-check-sa@the-financial-chameleon.iam.gserviceaccount.com`
- **Security**: No unauthenticated access allowed
- **Purpose**: Analyzes VOO stock data, Fear & Greed Index, and sends daily reports to Telegram

### Cloud Scheduler Job
- **Job Name**: `financial-chameleon-daily-check`
- **Location**: `asia-southeast1`
- **Schedule**: `0 20 * * 1-5` (8:00 PM Singapore time, weekdays only)
- **Target**: Cloud Run service URL (not Cloud Functions URL)
- **Authentication**: OIDC token with `cloud-scheduler-sa@the-financial-chameleon.iam.gserviceaccount.com`
- **HTTP Method**: POST

### Cloud Functions Gen 2 Deployment Best Practices

#### Pre-Deployment Checklist
```bash
# 1. Verify all service accounts exist
/home/cetyz/google-cloud-sdk/bin/gcloud iam service-accounts list --filter="email:(*fin-cham*|*cloud-scheduler*)"

# 2. Grant IAM permissions FIRST (prevents deployment failures)
/home/cetyz/google-cloud-sdk/bin/gcloud iam service-accounts add-iam-policy-binding \
  RUNTIME_SERVICE_ACCOUNT --member="serviceAccount:CURRENT_ADMIN_SA" --role="roles/iam.serviceAccountUser"

/home/cetyz/google-cloud-sdk/bin/gcloud iam service-accounts add-iam-policy-binding \
  SCHEDULER_SERVICE_ACCOUNT --member="serviceAccount:CURRENT_ADMIN_SA" --role="roles/iam.serviceAccountUser"
```

#### Standard Deployment Commands
```bash
# 1. Deploy Cloud Function Gen 2
cd daily-check
/home/cetyz/google-cloud-sdk/bin/gcloud functions deploy FUNCTION_NAME \
  --gen2 \
  --runtime=python311 \
  --source=. \
  --entry-point=main \
  --trigger-http \
  --service-account=RUNTIME_SERVICE_ACCOUNT \
  --region=asia-southeast1 \
  --memory=1Gi \
  --timeout=540s \
  --no-allow-unauthenticated

# 2. Get the Cloud Run URL (CRITICAL for Gen 2)
CLOUD_RUN_URL=$(/home/cetyz/google-cloud-sdk/bin/gcloud functions describe FUNCTION_NAME \
  --region=asia-southeast1 --format="value(serviceConfig.uri)")

# 3. Create Cloud Scheduler job with Cloud Run URL
/home/cetyz/google-cloud-sdk/bin/gcloud scheduler jobs create http FUNCTION_NAME \
  --location=asia-southeast1 \
  --schedule="CRON_EXPRESSION" \
  --time-zone="Asia/Singapore" \
  --uri="$CLOUD_RUN_URL" \
  --http-method=POST \
  --oidc-service-account-email=SCHEDULER_SERVICE_ACCOUNT \
  --oidc-token-audience="$CLOUD_RUN_URL"

# 4. Grant invoke permissions (Gen 2 uses Cloud Run permissions)
/home/cetyz/google-cloud-sdk/bin/gcloud functions add-invoker-policy-binding FUNCTION_NAME \
  --region=asia-southeast1 \
  --member="serviceAccount:SCHEDULER_SERVICE_ACCOUNT"
```

#### Critical Gen 2 Differences
- **URLs**: Gen 2 functions have TWO URLs - use the Cloud Run URL (`serviceConfig.uri`) for scheduler jobs
- **Permissions**: Use `roles/run.invoker` and `gcloud functions add-invoker-policy-binding`, NOT `roles/cloudfunctions.invoker`
- **Authentication**: OIDC audience must match the Cloud Run URL exactly
- **Trigger**: Use `--trigger-http` NOT `--trigger=https`

#### Testing & Validation
```bash
# Test scheduler job manually
/home/cetyz/google-cloud-sdk/bin/gcloud scheduler jobs run FUNCTION_NAME --location=asia-southeast1

# Check function logs
/home/cetyz/google-cloud-sdk/bin/gcloud functions logs read FUNCTION_NAME --region=asia-southeast1 --limit=10

# Verify scheduler job status
/home/cetyz/google-cloud-sdk/bin/gcloud scheduler jobs describe FUNCTION_NAME --location=asia-southeast1
```

#### Common Pitfalls to Avoid
1. **IAM Setup**: Always grant `iam.serviceAccountUser` to admin SA BEFORE deployment
2. **Wrong URL**: Never use Cloud Functions URL for scheduler jobs with Gen 2 functions
3. **Wrong Permissions**: Gen 2 functions require Cloud Run permissions, not Cloud Functions permissions
4. **Region Mismatch**: Ensure function and scheduler job are in the same region
5. **Authentication Issues**: Verify OIDC audience matches the exact Cloud Run URL

