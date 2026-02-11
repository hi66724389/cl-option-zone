"""
Core Volume Profile Algorithm
Calculates POC, VAH, VAL, HVN, LVN based on price-volume distribution.
"""

import pandas as pd
import numpy as np
from scipy.signal import find_peaks, savgol_filter
from typing import Dict, List, Tuple
import logging

class VolumeProfileAnalyzer:
    def __init__(self, df: pd.DataFrame, n_bins: int = 100, va_range: float = 0.70):
        """
        Args:
            df: DataFrame containing 'Close' and 'Volume'
            n_bins: Number of price bins (histogram resolution)
            va_range: Value Area percentage (default 70%)
        """
        self.df = df
        self.n_bins = n_bins
        self.va_range = va_range
        self.logger = logging.getLogger(__name__)
        
        # Calculation results
        self.profile = None
        self.poc_price = None
        self.vah = None
        self.val = None
        self.hvns = []
        self.lvns = []

    def calculate(self) -> Dict:
        """Execute the full volume profile analysis"""
        self._build_histogram()
        self._calculate_poc()
        self._calculate_value_area()
        self._identify_nodes()
        
        return self.get_results()

    def _build_histogram(self):
        """Create price-volume histogram"""
        # Determine price range
        price_min = self.df['Low'].min()
        price_max = self.df['High'].max()
        
        # Create bins
        bins = np.linspace(price_min, price_max, self.n_bins + 1)
        
        # Assign volume to bins
        # We assume volume occurred at the 'Close' price for simplicity in this version.
        # A more advanced version would distribute volume across High-Low range.
        self.df['bin_idx'] = np.digitize(self.df['Close'], bins)
        
        # Group by bin and sum volume
        grouped = self.df.groupby('bin_idx')['Volume'].sum()
        
        # Reindex to ensure all bins exist (even with 0 volume)
        all_bins = pd.Series(0, index=np.arange(1, self.n_bins + 2))
        self.profile = all_bins.add(grouped, fill_value=0)
        
        # Map bin index back to price
        self.bin_prices = {i: (bins[i-1] + bins[i])/2 for i in range(1, len(bins))}

    def _calculate_poc(self):
        """Find Point of Control (Max Volume)"""
        max_vol_idx = self.profile.idxmax()
        self.poc_price = self.bin_prices.get(max_vol_idx, 0.0)
        self.max_vol_idx = max_vol_idx

    def _calculate_value_area(self):
        """Calculate Value Area High (VAH) and Low (VAL)"""
        total_volume = self.profile.sum()
        target_volume = total_volume * self.va_range
        
        # Start from POC and expand
        current_volume = self.profile.loc[self.max_vol_idx]
        upper_idx = self.max_vol_idx
        lower_idx = self.max_vol_idx
        
        # Expansion loop
        while current_volume < target_volume:
            # Check next upper and lower bins
            next_upper = upper_idx + 1
            next_lower = lower_idx - 1
            
            vol_upper = self.profile.get(next_upper, 0)
            vol_lower = self.profile.get(next_lower, 0)
            
            # Expand towards the side with higher volume (standard VP logic)
            # Or expand both if we want strict symmetric search? 
            # Standard: Dual expansion usually favors the higher immediate neighbor
            
            if vol_upper > vol_lower:
                current_volume += vol_upper
                upper_idx = next_upper
            else:
                current_volume += vol_lower
                lower_idx = next_lower
                
            # Break if we hit boundaries
            if next_upper > self.n_bins and next_lower < 1:
                break
                
        self.vah = self.bin_prices.get(upper_idx, 0.0)
        self.val = self.bin_prices.get(lower_idx, 0.0)

    def _identify_nodes(self):
        """Identify High Volume Nodes (HVN) and Low Volume Nodes (LVN)"""
        # Smooth the profile for peak detection
        vol_array = self.profile.sort_index().values
        
        # Use Savitzky-Golay filter to smooth noise
        # window_length must be odd and <= len(x)
        window = min(11, len(vol_array))
        if window % 2 == 0: window -= 1
        
        if window > 3:
            smoothed_vol = savgol_filter(vol_array, window, 3)
        else:
            smoothed_vol = vol_array

        # Find Peaks (HVN)
        peaks, _ = find_peaks(smoothed_vol, prominence=np.max(smoothed_vol)*0.05) # 5% prominence
        self.hvns = [self.bin_prices.get(self.profile.index[i], 0.0) for i in peaks]
        
        # Find Valleys (LVN) - Invert signal
        valleys, _ = find_peaks(-smoothed_vol, prominence=np.max(smoothed_vol)*0.05)
        self.lvns = [self.bin_prices.get(self.profile.index[i], 0.0) for i in valleys]

    def get_results(self) -> Dict:
        return {
            "POC": round(self.poc_price, 2),
            "VAH": round(self.vah, 2),
            "VAL": round(self.val, 2),
            "HVNs": [round(x, 2) for x in self.hvns],
            "LVNs": [round(x, 2) for x in self.lvns],
            "Total_Volume": int(self.profile.sum())
        }
