# Weekly Insights Development Checklist

**Project Goal**: Build a GCP Cloud Function that runs every Sunday at 9pm Singapore time, analyzes weekly market data, and sends AI-generated summaries to the @thefinancialchameleon Telegram channel.

**Important Notes**:
- Each checklist item is a complete, executable AI developer prompt
- Follow the existing daily-check system patterns at `/daily-check/main.py`
- Use the same GCP project: "the-financial-chameleon"
- Reference CLAUDE.md, GCP_INSTRUCTIONS.md, and DEVELOPMENT_INSTRUCTIONS.md for guidance
- No coding should be done while creating this checklist

---

## Phase 1: Infrastructure Setup

### 1.1 Create Project Structure
- [ ] **Task**: Create the weekly-insights directory structure. In the `/weekly-insights/` folder, create these files: `main.py` (empty main function), `requirements.txt` (copy from daily-check and add google-generativeai), `config.py` (for storing constants like sector ETF tickers, API endpoints, message templates). Structure should mirror the daily-check folder exactly. Expected outcome: Complete folder structure ready for development.

### 1.2 Set Up Gemini API Integration  
- [ ] **Task**: Add Google Gemini API to the project. Install google-generativeai package, create a new secret in GCP Secret Manager named "gemini-api-key" using the gcloud CLI, write a function `get_gemini_api_key()` in main.py that retrieves this secret (follow the same pattern as `get_telegram_bot_token()` in daily-check/main.py), and test the connection with a simple API call. Expected outcome: Working Gemini API integration with secret management.

### 1.3 Create Weekly Insights Service Account
- [ ] **Task**: Create a new GCP service account specifically for weekly insights. Name it `weekly-insights-sa@the-financial-chameleon.iam.gserviceaccount.com`, assign it the `roles/secretmanager.secretAccessor` role, and grant the admin service account (`the-financial-chameleon-bf516ef64faa.json`) the `roles/iam.serviceAccountUser` permission on this new service account. Document the service account details in the config.py file. Expected outcome: Dedicated service account ready for Cloud Function deployment.

### 1.4 Configure Enhanced Cloud Function Environment
- [ ] **Task**: Prepare Cloud Function deployment configuration. Set memory allocation to 2Gi (double the daily-check due to data processing requirements), timeout to 540s, runtime to Python 3.11 Gen 2, region to asia-southeast1, entry point to main, and service account to the newly created weekly-insights-sa. Document these specifications in a deployment script or configuration file. Expected outcome: Cloud Function configuration ready for deployment.

### 1.5 Set Up Cloud Scheduler for Sunday Execution
- [ ] **Task**: Create a Cloud Scheduler job for weekly execution. Schedule: `0 21 * * 0` (9:00 PM Singapore time, Sundays only), location: asia-southeast1, target: Cloud Run service URL (will be generated after function deployment), authentication: OIDC token with the weekly-insights-sa service account, HTTP method: POST. Create the scheduler job creation command but do not execute until the function is deployed. Expected outcome: Scheduler configuration ready for activation.

### 1.6 Design Data Structure Templates
- [ ] **Task**: Create data structure templates in config.py. Define dictionaries for: major market indices (S&P 500, Dow, Nasdaq), API endpoints, and message template structures for both Movement Summary and Analytical Summary sections. Focus on broad market data rather than individual sectors or stocks. Expected outcome: Simplified data structure definitions focused on market movements.

---

## Phase 2: Data Collection Module

### 2.1 Adapt Existing Ticker Data Functions
- [ ] **Task**: Modify the existing `get_ticker_data()` function from daily-check/main.py for weekly analysis. Change the period parameter to '1y' for historical comparison, modify the interval to '1d' to get daily data within the year, add support for multiple tickers as input (list instead of single ticker), and return a dictionary with each ticker's data. Preserve the existing error handling and logging patterns. Expected outcome: Enhanced ticker data function supporting multiple securities and longer historical periods.

### 2.2 Remove Sector ETF Data Collection
- [ ] **Task**: Skip sector ETF data collection to focus on overall market movements. This phase will be removed from the implementation to maintain focus on broad market indices rather than individual sector analysis.

### 2.3 Remove Individual Stock Data Collection
- [ ] **Task**: Skip individual stock data collection to focus on overall market movements. This phase will be removed from the implementation to maintain focus on broad market indices rather than individual stock analysis.

### 2.4 Extend Fear & Greed Index for Weekly Analysis
- [ ] **Task**: Modify the existing `get_raw_historical_fng()` function from daily-check/main.py for weekly insights. Extend the data collection period to 30 days, create a new function `calculate_weekly_fng_average()` that aggregates daily readings into weekly averages, compare current week's average to historical weekly averages, and add trend analysis (increasing/decreasing fear or greed). Maintain the same CNN API integration pattern. Expected outcome: Weekly Fear & Greed Index analysis with historical context.

### 2.5 Remove Market Breadth Indicators
- [ ] **Task**: Skip detailed market breadth indicators to focus on basic market movements. This phase will be removed from the implementation to maintain focus on simple weekly performance data.

### 2.6 Create Simple Historical Context Function  
- [ ] **Task**: Write a function `get_basic_historical_context(weeks_back=12)` that provides simple historical context. Compare current week's performance to the same week in previous years (1-2 years back), calculate basic weekly performance comparisons, and return simple context data without complex statistical analysis. Use pandas datetime indexing for basic week matching. Expected outcome: Simple historical context function providing basic weekly comparison data.

### 2.7 Add Comprehensive Data Validation
- [ ] **Task**: Create a data validation module with function `validate_weekly_data(data_dict)`. Check for data completeness across all sources (minimum 80% data availability), validate data types and ranges (percentage changes within reasonable bounds), implement fallback strategies for missing data (interpolation or historical averages), add comprehensive logging for data quality issues, and create error alerts for critical data failures. Expected outcome: Robust data validation system ensuring analysis reliability.

### 2.8 Build Simplified Data Aggregation Pipeline
- [ ] **Task**: Create the main data orchestration function `aggregate_weekly_data()` that combines basic data sources. Call ticker data and Fear & Greed functions, merge data into a unified structure organized by categories (market overview, sentiment), calculate week-over-week changes for major indices, prepare data dictionaries optimized for Gemini API consumption, and add data export functionality for debugging. Expected outcome: Simplified data aggregation pipeline producing basic analysis datasets.

---

## Phase 3: Analysis Engine

### 3.1 Create Weekly Movement Summary Calculator
- [ ] **Task**: Build a basic movement summary function `calculate_weekly_movements()`. Calculate week-over-week percentage changes for major indices and key securities, identify the largest single-day moves within the week, compare current week's performance to previous weeks, and format the data for clear presentation. Focus on factual movement data without technical analysis interpretation. Expected outcome: Simple movement calculation providing weekly performance summary.

### 3.2 Build Market Overview Calculator  
- [ ] **Task**: Create `calculate_market_overview()` that provides basic market summary data. Calculate week-over-week percentage changes for major indices (S&P 500, Dow, Nasdaq), identify overall market direction (up/down for the week), compare current week's performance to recent weeks for context, and format data for clear presentation in the weekly summary. Focus on broad market movements without detailed statistical analysis. Expected outcome: Simple market overview providing weekly directional context.

### 3.3 Create Historical Context Calculator
- [ ] **Task**: Build `generate_weekly_context()` for basic historical comparison. Compare current week's performance to the same week in previous years (1-3 years back), identify if the current week was above or below average performance, provide simple context about how this week compares to recent weeks, and format the comparison data for easy reading. Focus on factual historical comparisons without complex pattern analysis. Expected outcome: Simple historical context providing weekly performance perspective.

### 3.4 Build Fear & Greed Weekly Summary
- [ ] **Task**: Create `summarize_weekly_fng()` for sentiment overview. Calculate average Fear & Greed Index for the current week, compare to previous week's average, identify overall sentiment direction (more fearful or greedy), and format the sentiment data for inclusion in the weekly summary. Keep analysis simple and factual without complex sentiment interpretation. Expected outcome: Basic sentiment summary providing weekly Fear & Greed context.

### 3.5 Remove Sector Analysis
- [ ] **Task**: Skip sector-specific analysis to focus on overall market movements. This phase will be removed from the implementation to maintain focus on broad market summary rather than sector rotation or individual sector performance analysis.

### 3.6 Remove Individual Stock Analysis
- [ ] **Task**: Skip individual company analysis to focus on overall market movements. This phase will be removed from the implementation to maintain focus on broad market summary rather than individual stock performance analysis.

### 3.7 Create Simple Data Aggregation
- [ ] **Task**: Build `aggregate_weekly_summary_data()` to combine all basic movement data. Gather weekly percentage changes, historical context, and Fear & Greed summary into a structured format suitable for content generation. Focus on organizing the factual data rather than complex analysis. Expected outcome: Clean data structure ready for AI content generation.

### 3.8 Finalize Movement Summary Data
- [ ] **Task**: Create `finalize_movement_data()` to prepare the final dataset for content generation. Combine weekly movement calculations, market overview, historical context, and sentiment data into a clean, organized structure. Ensure all data is properly formatted and ready for AI prompt injection. Expected outcome: Complete movement summary dataset ready for content generation.

---

## Phase 4: Content Generation

### 4.1 Design Gemini API Prompt Templates
- [ ] **Task**: Create sophisticated prompt engineering templates for content generation. Design a Movement Summary prompt template that includes data placeholders, formatting instructions, tone guidelines (professional but accessible), length constraints (150-200 words), and output structure requirements. Create an Analytical Summary prompt template with similar specifications but focused on deeper analysis (200-300 words). Include context injection patterns and response validation criteria. Expected outcome: Professional prompt templates optimized for consistent, high-quality financial content generation.

### 4.2 Create Movement Summary Generator
- [ ] **Task**: Build `generate_movement_summary(data)` for the first section of the weekly message. Format the week's percentage change data for clear presentation, describe the highest and lowest single-day moves with context, ensure the content is accessible to non-technical readers, and maintain a consistent weekly newsletter tone. Use the Gemini API with the Movement Summary prompt template and validate output format. Focus on factual movement data without technical analysis interpretation. Expected outcome: Automated Movement Summary generator producing consistent, readable weekly market overviews.

### 4.3 Create Analytical Summary Generator
- [ ] **Task**: Build `generate_analytical_summary(data)` for the second section. Generate historical comparison narratives using basic comparison data, provide context about weekly performance in plain language, maintain analytical depth while ensuring readability, and focus on overall market trends rather than specific sectors or stocks. Use the Analytical Summary prompt template and include fact-checking against source data. Expected outcome: Simplified Analytical Summary generator providing professional market commentary.

### 4.4 Build Content Validation System
- [ ] **Task**: Create `validate_generated_content()` for quality assurance. Cross-reference AI-generated statements against source data for factual accuracy, check for appropriate financial terminology usage and explanations, ensure content matches the established brand voice and tone, validate that statistical claims are properly supported, and flag any potentially misleading or oversimplified statements. Include readability scoring and technical accuracy checks. Expected outcome: Comprehensive content validation system ensuring professional quality and accuracy.

### 4.5 Create Message Formatting Module
- [ ] **Task**: Build `format_telegram_message()` for final message preparation. Combine Movement Summary and Analytical Summary with proper section headers, add appropriate emojis and visual elements for readability, ensure the message stays within Telegram's character limits, format technical data (percentages, numbers) consistently, and add footer elements (timestamp, data sources). Include message preview functionality for testing. Expected outcome: Professional message formatting system producing publication-ready weekly insights.

### 4.6 Add Content Quality Control Layer
- [ ] **Task**: Create `quality_check_content()` as the final content gate. Implement readability assessment using standard metrics (Flesch-Kincaid score), perform technical accuracy validation against source data, ensure brand voice consistency with previous messages, check for completeness of required sections and data points, and implement approval workflows for content review. Include logging and metrics for content quality tracking. Expected outcome: Quality control system ensuring consistent, professional weekly content delivery.

---

## Phase 5: Integration and Testing

### 5.1 Create Main Execution Flow
- [ ] **Task**: Build the orchestrating `main(request=None)` function following the daily-check pattern. Implement the complete pipeline: data collection → analysis → content generation → delivery, add comprehensive error handling with specific recovery strategies for each component, implement retry logic for API failures with exponential backoff, include execution timing and performance monitoring, and ensure graceful degradation when non-critical components fail. Follow the same logging patterns as daily-check/main.py. Expected outcome: Robust main execution function capable of reliable weekly operation.

### 5.2 Add Debugging and Monitoring System
- [ ] **Task**: Create comprehensive debugging infrastructure. Implement structured logging throughout the entire pipeline with different log levels, create debug message formatting for the test channel (@testchameleonchannel), add performance monitoring with execution time tracking for each component, implement error tracking with categorization and alerting, and create data dump functionality for troubleshooting. Include Cloud Logging integration following GCP best practices. Expected outcome: Complete monitoring and debugging system for operational excellence.

### 5.3 Create Local Testing Framework
- [ ] **Task**: Build local testing capabilities for development efficiency. Create test data generation utilities that simulate real market conditions, implement mock API responses for all external services (yfinance, CNN, Gemini), enable local execution without GCP dependencies using environment variables, create unit tests for all core functions with comprehensive coverage, and add integration test suites for component interactions. Include test data versioning for reproducible testing. Expected outcome: Comprehensive testing framework enabling rapid development and validation.

### 5.4 Implement Deployment Testing Protocol
- [ ] **Task**: Create systematic deployment testing procedures. Deploy the function to a test GCP environment, validate all integrations work correctly in the cloud environment (Secret Manager, Gemini API, Telegram), test scheduler trigger functionality manually using gcloud commands, verify message delivery to the test channel with proper formatting, and conduct end-to-end testing with real market data. Document deployment procedures and validation checklists. Expected outcome: Validated deployment process ensuring reliable production deployment.

### 5.5 Create Production Validation System
- [ ] **Task**: Establish production deployment and monitoring protocols. Deploy to the production GCP environment using the service accounts and configurations established in Phase 1, set up comprehensive monitoring using Cloud Monitoring with custom metrics and alerts, test the actual Sunday schedule with manual triggers, monitor the first several executions closely for any issues, and establish incident response procedures. Include rollback procedures and emergency contacts. Expected outcome: Production-ready system with full monitoring and operational procedures.

### 5.6 Add Long-term Monitoring and Maintenance
- [ ] **Task**: Create ongoing operational excellence systems. Set up Cloud Monitoring alerts for function failures, API quota issues, and performance degradation, create performance dashboards showing execution time, success rate, and content quality metrics, establish error notification systems for immediate issue awareness, document operational procedures for common maintenance tasks, and create quarterly review processes for content quality and system performance. Include cost monitoring and optimization recommendations. Expected outcome: Complete operational framework ensuring long-term system reliability and continuous improvement.

---

## Final Validation Checklist

### Pre-Production Validation
- [ ] All 34 tasks completed and validated
- [ ] End-to-end testing successful in test environment  
- [ ] Content quality approved by stakeholders
- [ ] Performance metrics within acceptable ranges
- [ ] Security review completed (no exposed secrets)
- [ ] Documentation complete and accessible
- [ ] Monitoring and alerting fully configured
- [ ] Rollback procedures tested and documented

### Production Readiness
- [ ] Production deployment successful
- [ ] First test execution sent to test channel
- [ ] Manual scheduler trigger test successful
- [ ] Production monitoring active and alerting
- [ ] Team trained on operational procedures
- [ ] Ready for first automated Sunday execution

**Target Completion**: 8 weeks from start
**Success Criteria**: Fully automated weekly insights delivered every Sunday at 9pm Singapore time to @thefinancialchameleon with professional quality market analysis powered by AI content generation.