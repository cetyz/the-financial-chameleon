import requests
import pandas as pd
from datetime import datetime, timedelta

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

    except KeyError as e:
        print(f"Error processing FNG data: {e}")
        return pd.DataFrame()

def get_fng_historical_data(start_date=None, days_back=5) -> pd.DataFrame:
    """
    Get historical Fear and Greed Index data from CNN's API.
    
    Args:
        start_date (str, optional): Start date in 'YYYY-MM-DD' format. 
                                   If None, will use days_back parameter.
        days_back (int): Number of days back from today to fetch data.
                        Only used if start_date is None.
        
    Returns:
        pd.DataFrame: DataFrame with columns ['date', 'fng_value', 'rating']
    """
    raw_data = get_raw_historical_fng(start_date, days_back)
    return process_fng(raw_data)

if __name__ == '__main__':

    df = get_fng_historical_data()
    print(df)