import requests
from datetime import datetime, timedelta

# data manipulation packages
import numpy as np
import pandas as pd

# financial imports
import fear_and_greed
import yfinance as yf

# telegram
import telegram


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
        
        # Drop duplicates if any
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
    
    # Add placeholder signal column
    df['signal'] = 'placeholder'  # TODO: implement strategy function to get signal
    
    return df

def process_data(ticker_df: pd.DataFrame, raw_fng_data: dict) -> pd.DataFrame:
    """
    Process raw ticker data and FNG data into a combined dataframe with all features.
    Returns only the last two complete rows.
    
    Args:
        ticker_df (pd.DataFrame): Raw ticker data from get_ticker_data()
        raw_fng_data (dict): Raw FNG data from get_raw_historical_fng()
        
    Returns:
        pd.DataFrame: Processed data with moving averages and FNG data (last 2 rows only)
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
        fng_df['date'] = pd.to_datetime(fng_df['date']).dt.date
        
        # Join FNG data with ticker data on date
        df_combined = df_with_ma.merge(fng_df, on='date', how='left')
    else:
        # If no FNG data, add empty FNG columns
        df_combined = df_with_ma.copy()
        df_combined['fng_value'] = np.nan
        df_combined['rating'] = 'Unknown'
    
    # Drop rows with missing moving average data
    df_complete = df_combined.dropna(subset=['50ma', '100ma', '200ma'])
    
    # Return only the last 2 rows
    return df_complete.tail(2)

def get_bull_bear(series) -> str:
    """
    Determine market sentiment based on price and moving averages from a pandas Series.
    
    Args:
        series (pd.Series): A row from the dataframe containing Close, 50ma, 200ma
        
    Returns:
        str: Market sentiment ('bull', 'bear', or 'neutral')
    """
    price = series['Close']
    ma50 = series['50ma']
    ma200 = series['200ma']
    
    # Handle missing data
    if pd.isna(price) or pd.isna(ma50) or pd.isna(ma200):
        return 'unknown'
    
    if (price > ma50) and (ma50 > ma200):
        return 'bull'
    elif (price < ma50) and (ma50 < ma200):
        return 'bear'
    else:
        return 'neutral'

if __name__ == '__main__':
    
    # get raw data
    raw_ticker_data = get_ticker_data('VOO')
    raw_fng_data = get_raw_historical_fng()

    # process data and get the last 2 complete rows
    processed_data = process_data(raw_ticker_data, raw_fng_data)
    
    # add signals to processed data
    final_data = add_signal(processed_data)

    print(f"Number of complete rows: {len(final_data)}")
    print("\nProcessed data:")
    print(final_data[['Close', '50ma', '200ma', 'signal', 'fng_value', 'rating']])

    sentiment = get_bull_bear(final_data.iloc[-1])
    print(sentiment)
    print(final_data)


    