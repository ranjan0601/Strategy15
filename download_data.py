
import yfinance as yf
import time
import random
import logging
from datetime import datetime

def download_stock_data(symbols, period="1y", max_retries=3):
    """
    Download historical data for a list of stock symbols with retry logic
    
    Parameters:
    symbols: List of stock symbols
    period: Time period to download (default "1y" = 1 year)
    max_retries: Number of download attempts before giving up
    
    Returns:
    Dictionary with stock symbols as keys and OHLC DataFrames as values
    """
    stock_data = {}
    
    # Configure logging
    logging.basicConfig(
        filename="stock_download.log",
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.info(f"Starting downloads for {len(symbols)} symbols at {datetime.now()}")
    
    for symbol in symbols:
        for attempt in range(max_retries):
            try:
                logging.info(f"Downloading {symbol} (attempt {attempt+1}/{max_retries})")
                
                # Use a custom header to avoid being blocked
                yf.Ticker(symbol).headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # Download with a timeout
                data = yf.download(
                    symbol, 
                    period=period, 
                    progress=False
                )
                
                if not data.empty:
                    # Process the data
                    result = data.reset_index(drop=False)
                    result.columns = range(result.shape[1])
                    result.rename(columns={
                        0: 'Date', 1: 'Close', 2: 'High', 
                        3: 'Low', 4: 'Open', 5: 'Volume'
                    }, inplace=True)
                    result.set_index('Date', inplace=True)
                    stock_data[symbol] = result
                    logging.info(f"Successfully downloaded {symbol} data")
                    break  # Success, exit retry loop
                else:
                    logging.warning(f"Download successful but no data for {symbol}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retrying
            
            except Exception as e:
                logging.error(f"Error downloading {symbol}: {str(e)}")
                if attempt < max_retries - 1:
                    # Exponential backoff
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logging.info(f"Waiting {delay:.2f} seconds before retry...")
                    time.sleep(delay)
                else:
                    logging.error(f"All {max_retries} attempts failed for {symbol}")
        
        # Add delay between symbols to avoid rate limiting
        time.sleep(1.5)
    
    logging.info(f"Download process completed at {datetime.now()}")
    return stock_data


# File path: d:\Python_Practice\Strategy15\main.py
# Content:
if __name__ == "__main__":
    # Example usage
    symbols = ["AAPL", "MSFT", "GOOGL"]
    stock_data = download_stock_data(symbols)
    print(stock_data)