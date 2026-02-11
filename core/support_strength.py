"""
Support/Resistance Strength Calculator
計算每個價位的支撐/壓力強度,並進行相對比較
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy.stats import zscore

class SupportStrengthAnalyzer:
    def __init__(self, df: pd.DataFrame, volume_profile: pd.Series, bin_prices: Dict):
        """
        Args:
            df: 原始OHLCV資料
            volume_profile: 從VolumeProfileAnalyzer取得的成交量分佈
            bin_prices: 價格區間對應表 {bin_idx: price}
        """
        self.df = df
        self.volume_profile = volume_profile
        self.bin_prices = bin_prices
        self.strength_scores = {}
        
    def calculate(self, current_price: float) -> Dict:
        """
        計算所有價位的支撐強度
        Returns:
            {
                'levels': [價格列表],
                'strengths': [強度分數列表],
                'normalized': [標準化分數列表],
                'ranks': [排名列表]
            }
        """
        # 1. 基於成交量計算基礎強度
        self._calculate_volume_strength()
        
        # 2. 基於歷史反彈次數調整強度
        self._adjust_by_bounces()
        
        # 3. 基於距離當前價格調整權重(越近越重要)
        self._adjust_by_distance(current_price)
        
        # 4. 標準化並排名
        results = self._normalize_and_rank()
        
        return results
    
    def _calculate_volume_strength(self):
        """基於成交量計算初始強度分數"""
        for bin_idx, volume in self.volume_profile.items():
            price = self.bin_prices.get(bin_idx, 0)
            if price > 0:
                # 基礎強度 = 成交量
                self.strength_scores[price] = float(volume)
    
    def _adjust_by_bounces(self):
        """
        計算每個價位的歷史反彈次數
        反彈定義: 價格觸及該區間後方向反轉
        """
        # 簡化版: 計算每個價位被測試的次數
        for price in self.strength_scores.keys():
            # 計算價格在該區間附近的K線數
            tolerance = price * 0.002  # ±0.2%容差
            touches = ((self.df['Low'] >= price - tolerance) & 
                      (self.df['Low'] <= price + tolerance)).sum()
            
            # 權重: 觸碰次數越多,強度越強
            bounce_factor = 1 + (touches * 0.1)  # 每次觸碰增加10%
            self.strength_scores[price] *= bounce_factor
    
    def _adjust_by_distance(self, current_price: float):
        """
        根據距離當前價格的遠近調整權重
        距離越近,重要性越高
        """
        for price in self.strength_scores.keys():
            distance_ratio = abs(price - current_price) / current_price
            
            # 距離衰減函數: 距離越遠,權重越低
            # 使用指數衰減: e^(-k*distance)
            decay_factor = np.exp(-5 * distance_ratio)  # k=5
            self.strength_scores[price] *= decay_factor
    
    def _normalize_and_rank(self) -> Dict:
        """標準化分數並排名"""
        # 轉換為DataFrame方便操作
        df = pd.DataFrame({
            'price': list(self.strength_scores.keys()),
            'strength': list(self.strength_scores.values())
        }).sort_values('price')
        
        # 標準化 (Z-score)
        df['z_score'] = zscore(df['strength'])
        
        # Min-Max標準化到0-100
        min_val = df['strength'].min()
        max_val = df['strength'].max()
        df['normalized'] = ((df['strength'] - min_val) / (max_val - min_val) * 100).round(2)
        
        # 排名 (分數越高排名越前)
        df['rank'] = df['normalized'].rank(ascending=False, method='min').astype(int)
        
        # 過濾掉強度太低的(保留Top 30%)
        threshold = df['normalized'].quantile(0.70)
        df_filtered = df[df['normalized'] >= threshold].copy()
        
        # 重新排名
        df_filtered['rank'] = df_filtered['normalized'].rank(ascending=False, method='min').astype(int)
        
        return {
            'levels': df_filtered['price'].round(2).tolist(),
            'strengths': df_filtered['strength'].round(0).tolist(),
            'normalized': df_filtered['normalized'].tolist(),
            'z_scores': df_filtered['z_score'].round(2).tolist(),
            'ranks': df_filtered['rank'].tolist(),
            'full_data': df  # 保留完整資料供繪圖使用
        }
    
    def get_top_n(self, results: Dict, n: int = 10, above_price: float = None) -> Dict:
        """
        取得前N個最強支撐位
        Args:
            results: calculate()的返回結果
            n: 取前幾名
            above_price: 如果指定,只取該價格以下的支撐位
        """
        df = pd.DataFrame({
            'price': results['levels'],
            'normalized': results['normalized'],
            'rank': results['ranks']
        })
        
        # 過濾條件
        if above_price:
            df = df[df['price'] < above_price]
        
        # 取前N
        df = df.nsmallest(n, 'rank')
        
        return {
            'levels': df['price'].tolist(),
            'scores': df['normalized'].tolist(),
            'ranks': df['rank'].tolist()
        }
