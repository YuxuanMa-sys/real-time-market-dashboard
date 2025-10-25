"""
Data validation and quality checks for the ETL pipeline
Ensures data integrity and identifies issues early
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from src.config import DATA_QUALITY_CONFIG

logger = logging.getLogger(__name__)

class DataValidator:
    """Data validation and quality assurance"""
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_price_data(self, df: pd.DataFrame) -> Dict:
        """
        Validate stock price data
        
        Args:
            df: Price data DataFrame
        
        Returns:
            Validation results dictionary
        """
        config = DATA_QUALITY_CONFIG['price_data']
        results = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check required columns
        missing_cols = [col for col in config['required_columns'] if col not in df.columns]
        if missing_cols:
            results['valid'] = False
            results['issues'].append(f"Missing required columns: {missing_cols}")
        
        if df.empty:
            results['valid'] = False
            results['issues'].append("DataFrame is empty")
            return results
        
        # Check for null values
        null_counts = df.isnull().sum()
        total_rows = len(df)
        
        for col, null_count in null_counts.items():
            null_percentage = (null_count / total_rows) * 100
            if null_percentage > config['max_null_percentage']:
                results['valid'] = False
                results['issues'].append(f"Column {col} has {null_percentage:.1f}% null values")
            elif null_percentage > 0:
                results['warnings'].append(f"Column {col} has {null_percentage:.1f}% null values")
        
        # Check price ranges
        if 'close' in df.columns:
            close_prices = df['close'].dropna()
            if len(close_prices) > 0:
                min_price = close_prices.min()
                max_price = close_prices.max()
                
                if min_price < config['min_price']:
                    results['valid'] = False
                    results['issues'].append(f"Minimum price {min_price} below threshold {config['min_price']}")
                
                if max_price > config['max_price']:
                    results['valid'] = False
                    results['issues'].append(f"Maximum price {max_price} above threshold {config['max_price']}")
                
                results['stats']['price_range'] = {'min': min_price, 'max': max_price}
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            results['warnings'].append(f"Found {duplicates} duplicate rows")
        
        # Check date consistency
        if 'date' in df.columns:
            dates = pd.to_datetime(df['date'])
            date_range = dates.max() - dates.min()
            results['stats']['date_range'] = {
                'start': dates.min(),
                'end': dates.max(),
                'days': date_range.days
            }
        
        # Check OHLC consistency
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            ohlc_issues = 0
            for _, row in df.iterrows():
                if pd.notna(row['open']) and pd.notna(row['high']) and pd.notna(row['low']) and pd.notna(row['close']):
                    if not (row['low'] <= row['open'] <= row['high'] and row['low'] <= row['close'] <= row['high']):
                        ohlc_issues += 1
            
            if ohlc_issues > 0:
                results['warnings'].append(f"Found {ohlc_issues} OHLC consistency issues")
        
        results['stats']['total_rows'] = total_rows
        results['stats']['unique_symbols'] = df['symbol'].nunique() if 'symbol' in df.columns else 0
        
        return results
    
    def validate_macro_data(self, df: pd.DataFrame) -> Dict:
        """
        Validate macroeconomic data
        
        Args:
            df: Macro data DataFrame
        
        Returns:
            Validation results dictionary
        """
        config = DATA_QUALITY_CONFIG['macro_data']
        results = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check required columns
        missing_cols = [col for col in config['required_columns'] if col not in df.columns]
        if missing_cols:
            results['valid'] = False
            results['issues'].append(f"Missing required columns: {missing_cols}")
        
        if df.empty:
            results['valid'] = False
            results['issues'].append("DataFrame is empty")
            return results
        
        # Check for null values
        null_counts = df.isnull().sum()
        total_rows = len(df)
        
        for col, null_count in null_counts.items():
            null_percentage = (null_count / total_rows) * 100
            if null_percentage > config['max_null_percentage']:
                results['valid'] = False
                results['issues'].append(f"Column {col} has {null_percentage:.1f}% null values")
            elif null_percentage > 0:
                results['warnings'].append(f"Column {col} has {null_percentage:.1f}% null values")
        
        # Check value ranges for specific indicators
        if 'indicator_id' in df.columns and 'value' in df.columns:
            for indicator, (min_val, max_val) in config['value_range'].items():
                indicator_data = df[df['indicator_id'] == indicator]['value'].dropna()
                if len(indicator_data) > 0:
                    if indicator_data.min() < min_val or indicator_data.max() > max_val:
                        results['warnings'].append(f"Indicator {indicator} values outside expected range [{min_val}, {max_val}]")
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            results['warnings'].append(f"Found {duplicates} duplicate rows")
        
        results['stats']['total_rows'] = total_rows
        results['stats']['unique_indicators'] = df['indicator_id'].nunique() if 'indicator_id' in df.columns else 0
        
        return results
    
    def validate_trends_data(self, df: pd.DataFrame) -> Dict:
        """
        Validate Google Trends data
        
        Args:
            df: Trends data DataFrame
        
        Returns:
            Validation results dictionary
        """
        config = DATA_QUALITY_CONFIG['trends_data']
        results = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check required columns
        missing_cols = [col for col in config['required_columns'] if col not in df.columns]
        if missing_cols:
            results['valid'] = False
            results['issues'].append(f"Missing required columns: {missing_cols}")
        
        if df.empty:
            results['valid'] = False
            results['issues'].append("DataFrame is empty")
            return results
        
        # Check for null values
        null_counts = df.isnull().sum()
        total_rows = len(df)
        
        for col, null_count in null_counts.items():
            null_percentage = (null_count / total_rows) * 100
            if null_percentage > config['max_null_percentage']:
                results['valid'] = False
                results['issues'].append(f"Column {col} has {null_percentage:.1f}% null values")
            elif null_percentage > 0:
                results['warnings'].append(f"Column {col} has {null_percentage:.1f}% null values")
        
        # Check score ranges
        if 'score' in df.columns:
            scores = df['score'].dropna()
            if len(scores) > 0:
                min_score = scores.min()
                max_score = scores.max()
                
                if min_score < 0 or max_score > 100:
                    results['warnings'].append(f"Score values outside expected range [0, 100]: [{min_score}, {max_score}]")
                
                results['stats']['score_range'] = {'min': min_score, 'max': max_score}
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            results['warnings'].append(f"Found {duplicates} duplicate rows")
        
        results['stats']['total_rows'] = total_rows
        results['stats']['unique_keywords'] = df['keyword'].nunique() if 'keyword' in df.columns else 0
        
        return results
    
    def validate_news_data(self, df: pd.DataFrame) -> Dict:
        """
        Validate news sentiment data
        
        Args:
            df: News data DataFrame
        
        Returns:
            Validation results dictionary
        """
        config = DATA_QUALITY_CONFIG['news_data']
        results = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check required columns
        missing_cols = [col for col in config['required_columns'] if col not in df.columns]
        if missing_cols:
            results['valid'] = False
            results['issues'].append(f"Missing required columns: {missing_cols}")
        
        if df.empty:
            results['valid'] = False
            results['issues'].append("DataFrame is empty")
            return results
        
        # Check for null values
        null_counts = df.isnull().sum()
        total_rows = len(df)
        
        for col, null_count in null_counts.items():
            null_percentage = (null_count / total_rows) * 100
            if null_percentage > config['max_null_percentage']:
                results['valid'] = False
                results['issues'].append(f"Column {col} has {null_percentage:.1f}% null values")
            elif null_percentage > 0:
                results['warnings'].append(f"Column {col} has {null_percentage:.1f}% null values")
        
        # Check sentiment ranges
        if 'vader_compound' in df.columns:
            sentiments = df['vader_compound'].dropna()
            if len(sentiments) > 0:
                min_sentiment = sentiments.min()
                max_sentiment = sentiments.max()
                
                if min_sentiment < -1 or max_sentiment > 1:
                    results['warnings'].append(f"Sentiment values outside expected range [-1, 1]: [{min_sentiment}, {max_sentiment}]")
                
                results['stats']['sentiment_range'] = {'min': min_sentiment, 'max': max_sentiment}
                results['stats']['avg_sentiment'] = sentiments.mean()
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            results['warnings'].append(f"Found {duplicates} duplicate rows")
        
        results['stats']['total_rows'] = total_rows
        results['stats']['unique_symbols'] = df['symbol'].nunique() if 'symbol' in df.columns else 0
        
        return results
    
    def validate_data_freshness(self, df: pd.DataFrame, max_age_hours: int = 24) -> Dict:
        """
        Validate data freshness
        
        Args:
            df: DataFrame with timestamp column
            max_age_hours: Maximum age in hours
        
        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'stats': {}
        }
        
        # Find timestamp column
        timestamp_cols = ['fetched_at', 'created_at', 'date']
        timestamp_col = None
        
        for col in timestamp_cols:
            if col in df.columns:
                timestamp_col = col
                break
        
        if not timestamp_col:
            results['warnings'].append("No timestamp column found")
            return results
        
        # Check data age
        timestamps = pd.to_datetime(df[timestamp_col])
        now = datetime.now()
        
        if timestamp_col == 'date':
            # For date columns, check if data is recent
            latest_date = timestamps.max()
            days_old = (now.date() - latest_date.date()).days
            if days_old > max_age_hours / 24:
                results['warnings'].append(f"Latest data is {days_old} days old")
        else:
            # For datetime columns, check hours
            latest_time = timestamps.max()
            hours_old = (now - latest_time).total_seconds() / 3600
            if hours_old > max_age_hours:
                results['warnings'].append(f"Latest data is {hours_old:.1f} hours old")
        
        results['stats']['latest_timestamp'] = timestamps.max()
        results['stats']['earliest_timestamp'] = timestamps.min()
        
        return results
    
    def generate_quality_report(self, validation_results: Dict) -> str:
        """
        Generate a human-readable quality report
        
        Args:
            validation_results: Dictionary of validation results
        
        Returns:
            Formatted quality report string
        """
        report = []
        report.append("=" * 50)
        report.append("DATA QUALITY REPORT")
        report.append("=" * 50)
        
        for data_type, results in validation_results.items():
            report.append(f"\n{data_type.upper()} DATA:")
            report.append("-" * 20)
            
            if results['valid']:
                report.append("✅ Status: VALID")
            else:
                report.append("❌ Status: INVALID")
            
            if results['issues']:
                report.append("\n🚨 Issues:")
                for issue in results['issues']:
                    report.append(f"  - {issue}")
            
            if results['warnings']:
                report.append("\n⚠️  Warnings:")
                for warning in results['warnings']:
                    report.append(f"  - {warning}")
            
            if results['stats']:
                report.append("\n📊 Statistics:")
                for stat, value in results['stats'].items():
                    report.append(f"  - {stat}: {value}")
        
        report.append("\n" + "=" * 50)
        return "\n".join(report)

def run_data_quality_checks(price_df: pd.DataFrame = None, 
                           macro_df: pd.DataFrame = None,
                           trends_df: pd.DataFrame = None,
                           news_df: pd.DataFrame = None) -> Dict:
    """
    Run comprehensive data quality checks
    
    Args:
        price_df: Price data DataFrame
        macro_df: Macro data DataFrame
        trends_df: Trends data DataFrame
        news_df: News data DataFrame
    
    Returns:
        Dictionary with all validation results
    """
    validator = DataValidator()
    results = {}
    
    if price_df is not None:
        logger.info("Validating price data...")
        results['price_data'] = validator.validate_price_data(price_df)
    
    if macro_df is not None:
        logger.info("Validating macro data...")
        results['macro_data'] = validator.validate_macro_data(macro_df)
    
    if trends_df is not None:
        logger.info("Validating trends data...")
        results['trends_data'] = validator.validate_trends_data(trends_df)
    
    if news_df is not None:
        logger.info("Validating news data...")
        results['news_data'] = validator.validate_news_data(news_df)
    
    # Generate overall report
    report = validator.generate_quality_report(results)
    logger.info(f"\n{report}")
    
    return results
