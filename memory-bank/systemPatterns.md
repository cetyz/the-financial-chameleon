# System Patterns - Daily Check Component

## Architecture
- **Cloud Function as Service**: Daily check runs as GCP Cloud Function Gen 2 triggered by Cloud Scheduler
- **Serverless Event-Driven**: Weekday cron job (8PM SGT) triggers analysis and conditional messaging
- **Multi-Channel Communication**: Separate Telegram channels for production (@thefinancialchameleon) and debug (@testchameleonchannel)

## Design Patterns
- **Strategy Pattern**: Signal generation using configurable thresholds (Fear & Greed < 40 = BUY, > 60 = WAIT)
- **Data Pipeline Pattern**: Raw data ’ Processing ’ Analysis ’ Conditional Action
- **Environment Abstraction**: Dual token management (GCP Secret Manager vs local .env)
- **State Comparison**: Signal change detection by comparing last two data points

## Data Flow
1. Fetch VOO ticker data (yfinance) + Fear & Greed Index (CNN API)
2. Calculate moving averages (50MA, 100MA, 200MA) 
3. Apply signal logic with sentiment analysis
4. Compare previous vs current signal
5. Send alerts only on signal changes

## Integration Patterns
- **API Gateway Pattern**: Direct HTTP requests to Telegram Bot API
- **Secret Management**: GCP Secret Manager for production, environment variables for local development
- **Error Handling**: Graceful degradation with empty DataFrames for missing FNG data