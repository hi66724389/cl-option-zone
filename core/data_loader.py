"""
Data Loader Module for CL (Crude Oil) Futures
Using yfinance as the primary data source.
"""

import yfinance as yf
import pandas as pd
from typing import Tuple, Optional
import logging

class DataLoader:
    def __init__(self, symbol: str = "CL=F"):
        self.symbol = symbol
        self.logger = logging.getLogger(__name__)

    def fetch_data(self, period: str = "5d", interval: str = "5m") -> pd.DataFrame:
        """
        Fetch OHLCV data from yfinance.
        
        Args:
            period: Data period to download (e.g., "1d", "5d", "1mo")
            interval: Data interval (e.g., "1m", "5m", "1h", "1d")
            
        Returns:
            DataFrame with columns: [Open, High, Low, Close, Volume]
        """
        self.logger.info(f"Fetching {self.symbol} data (Period: {period}, Interval: {interval})...")
        
        try:
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for {self.symbol}")
                
            # Clean data
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df.index = pd.to_datetime(df.index)
            
            # Ensure proper timezone (UTC -> Local if needed, keeping UTC for analysis)
            if df.index.tz is None:
                df.index = df.index.tz_localize('UTC')
            
            self.logger.info(f"Successfully loaded {len(df)} rows.")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            raise

    def get_latest_price(self) -> float:
        """Get the current live price (delayed)"""
        ticker = yf.Ticker(self.symbol)
        # Fast retrieval
        todays_data = ticker.history(period='1d')
        return todays_data['Close'].iloc[-1]
