"""
Utility functions for data analysis and visualization
Common calculations and helper functions for the dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def calculate_returns(prices: pd.Series, periods: int = 1) -> pd.Series:
    """
    Calculate percentage returns for a price series
    
    Args:
        prices: Price series
        periods: Number of periods to look back
    
    Returns:
        Returns series
    """
    return prices.pct_change(periods=periods)

def calculate_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate rolling volatility (standard deviation)
    
    Args:
        returns: Returns series
        window: Rolling window size
    
    Returns:
        Volatility series
    """
    return returns.rolling(window=window).std() * np.sqrt(252)

def calculate_drawdown(prices: pd.Series) -> pd.Series:
    """
    Calculate rolling maximum drawdown
    
    Args:
        prices: Price series
    
    Returns:
        Drawdown series (negative values)
    """
    rolling_max = prices.expanding().max()
    drawdown = (prices - rolling_max) / rolling_max
    return drawdown

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: Returns series
        risk_free_rate: Risk-free rate (annual)
    
    Returns:
        Sharpe ratio
    """
    excess_returns = returns - risk_free_rate / 252
    return excess_returns.mean() / returns.std() * np.sqrt(252)

def calculate_beta(asset_returns: pd.Series, market_returns: pd.Series) -> float:
    """
    Calculate beta coefficient
    
    Args:
        asset_returns: Asset returns
        market_returns: Market returns (e.g., S&P 500)
    
    Returns:
        Beta coefficient
    """
    covariance = np.cov(asset_returns, market_returns)[0, 1]
    market_variance = np.var(market_returns)
    return covariance / market_variance

def calculate_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix for returns
    
    Args:
        returns_df: DataFrame with returns for multiple assets
    
    Returns:
        Correlation matrix
    """
    return returns_df.corr()

def calculate_sector_performance(prices_df: pd.DataFrame, sectors_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate sector-level performance metrics
    
    Args:
        prices_df: DataFrame with price data
        sectors_df: DataFrame with sector information
    
    Returns:
        Sector performance DataFrame
    """
    # Merge price and sector data
    merged_df = prices_df.merge(sectors_df, on='symbol', how='left')
    
    # Calculate sector performance
    sector_perf = merged_df.groupby(['sector', 'date']).agg({
        'close': 'mean',
        'volume': 'sum'
    }).reset_index()
    
    # Calculate returns by sector
    sector_perf['sector_return'] = sector_perf.groupby('sector')['close'].pct_change()
    
    return sector_perf

def calculate_moving_averages(prices: pd.Series, windows: List[int] = [20, 50, 200]) -> pd.DataFrame:
    """
    Calculate multiple moving averages
    
    Args:
        prices: Price series
        windows: List of window sizes
    
    Returns:
        DataFrame with moving averages
    """
    ma_df = pd.DataFrame(index=prices.index)
    ma_df['price'] = prices
    
    for window in windows:
        ma_df[f'ma_{window}'] = prices.rolling(window=window).mean()
    
    return ma_df

def detect_anomalies(returns: pd.Series, threshold: float = 3.0) -> pd.Series:
    """
    Detect anomalous returns using z-score
    
    Args:
        returns: Returns series
        threshold: Z-score threshold for anomaly detection
    
    Returns:
        Boolean series indicating anomalies
    """
    z_scores = np.abs((returns - returns.mean()) / returns.std())
    return z_scores > threshold

def calculate_sentiment_score(sentiment_df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """
    Calculate rolling sentiment scores
    
    Args:
        sentiment_df: DataFrame with sentiment data
        window: Rolling window size
    
    Returns:
        DataFrame with sentiment scores
    """
    sentiment_df = sentiment_df.copy()
    sentiment_df['sentiment_score'] = sentiment_df.groupby('symbol')['vader_compound'].rolling(
        window=window
    ).mean().reset_index(0, drop=True)
    
    return sentiment_df

def calculate_trend_strength(trends_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate trend strength indicators
    
    Args:
        trends_df: DataFrame with Google Trends data
    
    Returns:
        DataFrame with trend strength metrics
    """
    trends_df = trends_df.copy()
    
    # Calculate trend momentum
    trends_df['trend_momentum'] = trends_df.groupby('keyword')['score'].pct_change()
    
    # Calculate trend acceleration
    trends_df['trend_acceleration'] = trends_df.groupby('keyword')['trend_momentum'].diff()
    
    # Calculate trend strength (normalized)
    trends_df['trend_strength'] = trends_df.groupby('keyword')['score'].transform(
        lambda x: (x - x.min()) / (x.max() - x.min())
    )
    
    return trends_df

def calculate_macro_correlations(macro_df: pd.DataFrame, price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlations between macro indicators and market performance
    
    Args:
        macro_df: DataFrame with macroeconomic data
        price_df: DataFrame with price data
    
    Returns:
        Correlation DataFrame
    """
    # Calculate market returns
    market_returns = price_df[price_df['symbol'] == 'SPY'].set_index('date')['close'].pct_change()
    
    # Calculate correlations
    correlations = []
    for indicator in macro_df['indicator_id'].unique():
        indicator_data = macro_df[macro_df['indicator_id'] == indicator].set_index('date')['value']
        
        # Align dates and calculate correlation
        aligned_data = pd.concat([market_returns, indicator_data], axis=1, join='inner')
        correlation = aligned_data.corr().iloc[0, 1]
        
        correlations.append({
            'indicator_id': indicator,
            'correlation': correlation,
            'abs_correlation': abs(correlation)
        })
    
    return pd.DataFrame(correlations).sort_values('abs_correlation', ascending=False)

def generate_market_summary(price_df: pd.DataFrame, sentiment_df: pd.DataFrame) -> Dict:
    """
    Generate a summary of current market conditions
    
    Args:
        price_df: DataFrame with price data
        sentiment_df: DataFrame with sentiment data
    
    Returns:
        Dictionary with market summary metrics
    """
    latest_date = price_df['date'].max()
    latest_data = price_df[price_df['date'] == latest_date]
    
    # Market performance
    spy_data = latest_data[latest_data['symbol'] == 'SPY']
    market_performance = spy_data['close'].iloc[0] if not spy_data.empty else None
    
    # Sector performance
    sector_perf = latest_data.groupby('symbol')['close'].first()
    
    # Sentiment summary
    latest_sentiment = sentiment_df[sentiment_df['fetched_at'].dt.date == latest_date.date()]
    avg_sentiment = latest_sentiment['vader_compound'].mean() if not latest_sentiment.empty else None
    
    summary = {
        'date': latest_date,
        'market_performance': market_performance,
        'sector_count': len(sector_perf),
        'avg_sentiment': avg_sentiment,
        'sentiment_count': len(latest_sentiment),
        'market_status': 'Open' if latest_date.weekday() < 5 else 'Closed'
    }
    
    return summary

def validate_data_quality(df: pd.DataFrame, required_columns: List[str]) -> Dict:
    """
    Validate data quality and completeness
    
    Args:
        df: DataFrame to validate
        required_columns: List of required columns
    
    Returns:
        Dictionary with validation results
    """
    validation_results = {
        'total_rows': len(df),
        'missing_columns': [],
        'null_counts': {},
        'duplicate_rows': 0,
        'data_types': {}
    }
    
    # Check required columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    validation_results['missing_columns'] = missing_cols
    
    # Check null values
    for col in df.columns:
        null_count = df[col].isnull().sum()
        validation_results['null_counts'][col] = null_count
    
    # Check duplicates
    validation_results['duplicate_rows'] = df.duplicated().sum()
    
    # Check data types
    validation_results['data_types'] = df.dtypes.to_dict()
    
    return validation_results
