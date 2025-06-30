# data manipulation packages
import numpy as np
import pandas as pd

# financial imports
import fear_and_greed
import yfinance as yf

# telegram
import telegram


def get_moving_averages(ticker) -> dict:
    """
    Calculate moving averages for a given stock ticker.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'VOO', 'AAPL')
        
    Returns:
        dict: Dictionary containing price, ma50, ma100, ma200 values
    """
    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(period='201d')

    df['50ma'] = df['Close'].rolling(window=50, center=False).mean()
    df['100ma'] = df['Close'].rolling(window=100, center=False).mean()
    df['200ma'] = df['Close'].rolling(window=200, center=False).mean()
    
    price = df.iloc[-1]['Close']
    ma50 = df.iloc[-1]['50ma']
    ma100 = df.iloc[-1]['100ma']
    ma200 = df.iloc[-1]['200ma']

    data = {
        'price': price,
        'ma50': ma50,
        'ma100': ma100,
        'ma200': ma200,
    }

    return data


def get_bull_bear(price, ma50, ma200) -> str:
    """
    Determine market sentiment based on price and moving averages.
    
    Args:
        price (float): Current stock price
        ma50 (float): 50-day moving average
        ma200 (float): 200-day moving average
        
    Returns:
        str: Market sentiment ('bull', 'bear', or 'neutral')
    """
    if (price > ma50) and (ma50 > ma200):
        return 'bull'
    elif (price < ma50) and (ma50 < ma200):
        return 'bear'
    else:
        return 'neutral'

if __name__ == '__main__':
    
    price_data = get_moving_averages('VOO')
    ma50 = price_data['ma50']
    ma200 = price_data['ma200']
    price = price_data['price']
    bull_bear = get_bull_bear(price, ma50, ma200)

    print(price)
    print(ma50)
    print(ma200)
    print(bull_bear)

    