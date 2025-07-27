# GCP_INSTRUCTIONS.md

This file provides guidance for Google Cloud Platform operations in this repository.

## Configuration

- Telegram bot tokens stored in Google Cloud Secret Manager
- Project ID: "the-financial-chameleon"
- Bot names: 'financial-chameleon', 'trading-chameleon', 'crypto-chameleon'
- Main channel: '@thefinancialchameleon'
- Debug channel: '@testchameleonchannel'

## GCP Service Accounts

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

## Google Cloud CLI

- **CRITICAL**: Always use the WSL installation of gcloud, not the Windows installation
- **REQUIRED**: Use the full path `/home/cetyz/google-cloud-sdk/bin/gcloud` for all gcloud commands to avoid conflicts with Windows installation
- Ensure `gcloud` commands are run within the WSL environment to maintain consistency with the project setup

## Bash Tool Timeout Requirements

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