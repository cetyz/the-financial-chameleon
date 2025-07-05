import requests
from datetime import datetime, timedelta

# data manipulation packages
import numpy as np
import pandas as pd

# financial imports
import fear_and_greed
import yfinance as yf

# telegram - using requests for synchronous HTTP calls


def get_ticker_data(ticker) -> pd.DataFrame:
    """
    Get raw ticker data from yfinance.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'VOO', 'AAPL')
        
    Returns:
        pd.DataFrame: Raw price data with OHLCV columns
    """

    ticker_data = yf.Ticker(ticker)
    return ticker_data.history(period='201d')

def get_raw_historical_fng(start_date=None, days_back=5) -> dict:
    """
    Get raw historical Fear and Greed Index data from CNN's API.
    
    Args:
        start_date (str, optional): Start date in 'YYYY-MM-DD' format. 
                                   If None, will use days_back parameter.
        days_back (int): Number of days back from today to fetch data.
                        Only used if start_date is None.
        
    Returns:
        dict: Raw JSON data from the API
    """    

    # If no start_date provided, calculate it based on days_back
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    # CNN API endpoint
    base_url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    url = f"{base_url}/{start_date}"

    try:
        # Make request with headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }      
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching FNG data: {e}")
        return {}
    except KeyError as e:
        print(f"Error parsing FNG data: {e}")
        return {}

def process_fng(raw_data: dict) -> pd.DataFrame:
    """
    Process raw Fear and Greed Index data into a DataFrame.
    
    Args:
        raw_data (dict): Raw JSON data from the CNN API
        
    Returns:
        pd.DataFrame: DataFrame with columns ['date', 'fng_value', 'rating']
    """
    if not raw_data:
        return pd.DataFrame()
    
    try:
        # Extract historical data
        historical_data = raw_data['fear_and_greed_historical']['data']
        
        # Create DataFrame
        fng_df = pd.DataFrame(historical_data)
        
        # Convert timestamp to readable date
        fng_df['x'] = pd.to_datetime(fng_df['x'], unit='ms')
        fng_df = fng_df.rename(columns={'x': 'date', 'y': 'fng_value'})
        
        # Normalize date to just date part (removes time component)
        fng_df['date'] = fng_df['date'].dt.date
        
        # Add rating column based on fng_value
        def get_rating(value):
            if value <= 25:
                return "Extreme Fear"
            elif value <= 45:
                return "Fear"
            elif value <= 55:
                return "Neutral"
            elif value <= 75:
                return "Greed"
            else:
                return "Extreme Greed"
        
        fng_df['rating'] = fng_df['fng_value'].apply(get_rating)
        
        # Reset index to have date as a column
        fng_df = fng_df.reset_index(drop=True)
        
        # Sort by date
        fng_df = fng_df.sort_values('date')
        
        # Drop duplicates by date, keeping the last (most recent) entry
        fng_df = fng_df.drop_duplicates(subset=['date'], keep='last')
        
        return fng_df[['date', 'fng_value', 'rating']]
    
    except (KeyError, ValueError) as e:
        print(f"Error processing FNG data: {e}")
        return pd.DataFrame()

def add_moving_averages(ticker_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add moving averages to ticker data.
    
    Args:
        ticker_df (pd.DataFrame): Raw ticker data
        
    Returns:
        pd.DataFrame: Ticker data with moving averages added
    """
    df = ticker_df.copy()
    
    # Calculate moving averages
    df['50ma'] = df['Close'].rolling(window=50, center=False).mean()
    df['100ma'] = df['Close'].rolling(window=100, center=False).mean()
    df['200ma'] = df['Close'].rolling(window=200, center=False).mean()
    
    return df

def add_signal(processed_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add signal column to processed dataframe.
    
    Args:
        processed_df (pd.DataFrame): Processed dataframe with ticker data, moving averages, and FNG data
        
    Returns:
        pd.DataFrame: Dataframe with signal column added
    """
    df = processed_df.copy()
    
    df['signal'] = np.where(
        # always 'buy' signal when market is fearful
        df['fng_value'] < 40, 'BUY', np.where(
            # always 'wait' signal when market is greedy
            df['fng_value'] > 60, 'WAIT', np.where(
                # if neutral, only buy based on moving average conditions
                (df['Close'] > df['200ma']) & (df['Close'] < df['50ma']) & (df['50ma'] > df['200ma']), 'BUY', 'WAIT'
            )
        )
    )
    
    return df

def process_data(ticker_df: pd.DataFrame, raw_fng_data: dict) -> pd.DataFrame:
    """
    Process raw ticker data and FNG data into a combined dataframe with all features.
    Returns only the last two complete rows with bull/bear sentiment included.
    
    Args:
        ticker_df (pd.DataFrame): Raw ticker data from get_ticker_data()
        raw_fng_data (dict): Raw FNG data from get_raw_historical_fng()
        
    Returns:
        pd.DataFrame: Processed data with moving averages, FNG data, and bull/bear sentiment (last 2 rows only)
    """
    # Process FNG data
    fng_df = process_fng(raw_fng_data)
    
    # Add moving averages to ticker data
    df_with_ma = add_moving_averages(ticker_df)
    
    # Prepare ticker data for joining
    df_with_ma = df_with_ma.reset_index()
    df_with_ma['date'] = pd.to_datetime(df_with_ma['Date']).dt.date
    
    # Prepare FNG data for joining
    if not fng_df.empty:
        # Join FNG data with ticker data on date
        df_combined = df_with_ma.merge(fng_df, on='date', how='left')
    else:
        # If no FNG data, add empty FNG columns
        df_combined = df_with_ma.copy()
        df_combined['fng_value'] = np.nan
        df_combined['rating'] = 'Unknown'
    
    # Drop rows with missing moving average data
    df_complete = df_combined.dropna(subset=['50ma', '100ma', '200ma'])
    
    # Add bull/bear sentiment
    df_with_sentiment = add_bull_bear(df_complete)
    
    # Return only the last 2 rows
    return df_with_sentiment.tail(2)

def add_bull_bear(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add bull/bear sentiment column to dataframe based on price and moving averages.
    
    Args:
        df (pd.DataFrame): DataFrame that must contain columns 'Close', '50ma', '200ma'
        
    Returns:
        pd.DataFrame: DataFrame with 'bullbear' column added
        
    Raises:
        ValueError: If required columns are missing from the dataframe
    """
    # Check for required columns
    required_columns = ['Close', '50ma', '200ma']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"DataFrame is missing required columns: {missing_columns}")
    
    df_copy = df.copy()
    
    def determine_sentiment(row):
        price = row['Close']
        ma50 = row['50ma']
        ma200 = row['200ma']
        
        # Handle missing data
        if pd.isna(price) or pd.isna(ma50) or pd.isna(ma200):
            return 'unknown'
        
        if (price > ma50) and (ma50 > ma200):
            return 'bull'
        elif (price < ma50) and (ma50 < ma200):
            return 'bear'
        else:
            return 'neutral'
    
    df_copy['bullbear'] = df_copy.apply(determine_sentiment, axis=1)
    return df_copy

def access_secret(secret_name):

    from google.cloud import secretmanager

    secret_dict = {
        'financial-chameleon': 'the-financial-chameleon-tele-bot',
        'trading-chameleon': 'the-trading-chameleon-tele-bot',
        'crypto-chameleon': 'the-crypto-chameleon-tele-bot'
    }

    client = secretmanager.SecretManagerServiceClient()
    project_id = "the-financial-chameleon"
    secret_id = secret_dict[secret_name]
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})

    return response.payload.data.decode('UTF-8')

def get_telebot_token(bot_name):
    import os
    
    # Check if running in GCP Cloud Functions (multiple environment variables indicate GCP)
    if (os.getenv('GOOGLE_CLOUD_PROJECT') or 
        os.getenv('FUNCTION_NAME') or 
        os.getenv('K_SERVICE') or 
        os.getenv('GCLOUD_PROJECT')):
        # Running in GCP, use Secret Manager
        return access_secret(bot_name)
    else:
        # Running locally, use environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        token_dict = {
            'financial-chameleon': 'F_TELEBOT_TOKEN',
            'trading-chameleon': 'T_TELEBOT_TOKEN',
            'crypto-chameleon': 'C_TELEBOT_TOKEN',
        }
        
        env_var_name = token_dict.get(bot_name)
        if not env_var_name:
            raise ValueError(f"Unknown bot name: {bot_name}")
            
        token = os.getenv(env_var_name)
        if not token:
            raise ValueError(f"Token not found for {bot_name}. Check your .env file for {env_var_name}")
            
        return token

def send_message(bot_name, chat_id, msg, parse_mode=None):
    token = get_telebot_token(bot_name)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    data = {
        'chat_id': chat_id,
        'text': msg
    }
    
    if parse_mode:
        data['parse_mode'] = parse_mode
    
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()

def send_signal_change_message(bot_name, chat_id, current_signal, current_row, debug=False):
    """Send signal change message to telegram channel"""
    # Choose emoji based on signal
    if current_signal == 'BUY':
        signal_emoji = "🟢"
    else:  # WAIT
        signal_emoji = "🔴"
    
    # Generate qualitative message based on signal and market conditions
    def get_qualitative_message(signal, row):
        fng_value = row['fng_value']
        
        if signal == 'BUY':
            if fng_value < 40:
                return "Market fear has created a buying opportunity. Time to consider accumulating positions."
            else:
                return "Technical conditions have aligned favorably. Market positioning looks attractive for entry."
        else:  # WAIT
            if fng_value > 60:
                return "Market greed suggests caution. Consider waiting for better entry points."
            else:
                return "Technical conditions no longer favor entry. Patience may be rewarded."
    
    qualitative_msg = get_qualitative_message(current_signal, current_row)
    
    # Build main channel announcement message
    telegram_msg = ""
    if debug:
        telegram_msg += "[DEBUGGING MESSAGE]\n\n"
    telegram_msg += f"🦎 SIGNAL SHIFT 🦎\n\n"
    telegram_msg += f"{signal_emoji} New Signal: {current_signal}\n\n"
    telegram_msg += f"{qualitative_msg}\n\n"
    telegram_msg += f"🔔 Stay adaptable to market shifts with @thefinancialchameleon"
    
    # Send to main channel
    send_message(bot_name, chat_id, telegram_msg)

def main(request=None):
    """Cloud Function entry point and main logic"""
    
    # get raw data
    raw_ticker_data = get_ticker_data('VOO')
    raw_fng_data = get_raw_historical_fng()

    # process data and get the last 2 complete rows
    processed_data = process_data(raw_ticker_data, raw_fng_data)
    
    # add signals to processed data
    final_data = add_signal(processed_data)
    
    # Ensure we have exactly 2 rows for signal comparison
    if len(final_data) != 2:
        raise ValueError(f"Expected exactly 2 rows for analysis, got {len(final_data)}")

    # Check if signal changed between the two rows
    signals = final_data['signal'].tolist()
    if signals[0] == signals[1]:
        signal_change_msg = "Signal unchanged. No message sent to main channel.\n\n"
    else:
        signal_change_msg = f"❗ Signal changed! Signal is now {signals[1]}. Update will be sent to main channel. ❗\n\n"

        # Send signal change message to main channel
        current_signal = signals[1]
        current_row = final_data.iloc[1]
        
        send_signal_change_message(
            bot_name='financial-chameleon',
            chat_id='@thefinancialchameleon',
            current_signal=current_signal,
            current_row=current_row
        )
    
    # Convert final_data to simple string for Telegram message
    telegram_debug_msg = signal_change_msg + "═" * 15 + "\n\n" + f"📊 VOO Analysis ({len(final_data)} rows)\n\n"
    
    for _, row in final_data.iterrows():
        telegram_debug_msg += f"Date: {row['date']}\n"
        telegram_debug_msg += f"Close: ${row['Close']:.2f}\n"
        telegram_debug_msg += f"50MA: ${row['50ma']:.2f}\n"
        telegram_debug_msg += f"200MA: ${row['200ma']:.2f}\n"
        telegram_debug_msg += f"Sentiment: {row['bullbear']}\n"
        telegram_debug_msg += f"F&G: {row['fng_value']} ({row['rating']})\n"
        telegram_debug_msg += f"Signal: {row['signal']}\n"
        telegram_debug_msg += "─" * 15 + "\n"
    
    # Send message via Telegram
    send_message(
        bot_name='financial-chameleon',
        chat_id='@testchameleonchannel',
        msg=telegram_debug_msg
    )

    # Debug test
    debug = False
    if debug:
        # Calculate the actual current signal from the data
        current_signal = final_data.iloc[1]['signal']
        current_row = final_data.iloc[1]
        
        send_signal_change_message(
            bot_name='financial-chameleon',
            chat_id='@testchameleonchannel',
            current_signal=current_signal,
            current_row=current_row,
            debug=True
        )
    
    return "Daily check completed successfully"

if __name__ == '__main__':
    main()


    