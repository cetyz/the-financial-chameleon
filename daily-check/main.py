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

def process_data(ticker_df) -> pd.DataFrame:
    """
    Process ticker data to calculate moving averages and signals.
    Returns only the last two complete rows.
    
    Args:
        ticker_df (pd.DataFrame): Raw ticker data from get_ticker_data()
        
    Returns:
        pd.DataFrame: Processed data with moving averages and signals (last 2 rows only)
    """
    df = ticker_df.copy()

    # Calculate moving averages
    df['50ma'] = df['Close'].rolling(window=50, center=False).mean()
    df['100ma'] = df['Close'].rolling(window=100, center=False).mean()
    df['200ma'] = df['Close'].rolling(window=200, center=False).mean()

    # Calculate signals for each row
    df['signal'] = 'placeholder' # TODO: implement strategy function to get signal

    # Drop rows with missing moving average data
    df_complete = df.dropna()    

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
    raw_data = get_ticker_data('VOO')

    # process data and get the last 2 complete rows
    processed_data = process_data(raw_data)

    print(f"Number of complete rows: {len(processed_data)}")
    print("\nProcessed data:")
    print(processed_data[['Close', '50ma', '200ma', 'signal']])

    sentiment = get_bull_bear(processed_data.iloc[-1])
    print(sentiment)


    