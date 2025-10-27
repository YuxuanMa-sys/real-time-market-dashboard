"""
Configuration file for the Real-Time Market Dashboard
Contains all settings, constants, and configuration parameters
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    'dsn': os.getenv('PG_DSN'),
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
    'pool_recycle': 3600
}

# API Configuration
API_CONFIG = {
    'fred_api_key': os.getenv('FRED_API_KEY'),
    'news_api_key': os.getenv('NEWS_API_KEY'),
    'rate_limit_delay': 1,  # seconds between API calls
    'max_retries': 3,
    'timeout': 30
}

# Data Sources Configuration
SYMBOLS = {
    'indices': ['SPY', 'QQQ', 'IWM', 'EFA', 'VTI'],
    'sectors': ['XLF', 'XLK', 'XLE', 'XLI', 'XLV', 'XLY', 'XLP', 'XLU', 'XLB', 'XLRE'],
    'volatility': ['^VIX'],
    'all': ['SPY', 'QQQ', 'IWM', 'EFA', 'VTI', 'XLF', 'XLK', 'XLE', 'XLI', 'XLV', 
            'XLY', 'XLP', 'XLU', 'XLB', 'XLRE', '^VIX']
}

MACRO_INDICATORS = {
    'inflation': ['CPIAUCSL', 'CPILFESL'],
    'employment': ['UNRATE', 'PAYEMS', 'JOBOPENINGS'],
    'interest_rates': ['FEDFUNDS', 'DGS10', 'DGS2', 'DGS30'],
    'sentiment': ['UMCSENT', 'UMCSENT1'],
    'economic_activity': ['GDP', 'INDPRO', 'RETAILSALES'],
    'housing': ['HOUSINGSTARTS', 'CSUSHPISA'],
    'money_supply': ['M2SL', 'M1SL'],
    'all': ['CPIAUCSL', 'UNRATE', 'FEDFUNDS', 'UMCSENT', 'DGS10', 'DGS2', 'DGS30',
            'GDP', 'PAYEMS', 'INDPRO', 'RETAILSALES', 'HOUSINGSTARTS', 'DURABLE',
            'CAPACITY', 'M2SL', 'TOTALSA', 'CSUSHPISA', 'RECPROUSM156N', 'T10Y2Y', 'T10Y3M']
}

TRENDS_KEYWORDS = {
    'market_sentiment': [
        'stock market crash', 'recession', 'inflation', 'bear market', 'bull market'
    ],
    'investment_terms': [
        'buy stocks', 'sell stocks', 'stock market news', 'market volatility', 'fed interest rates'
    ],
    'economic_indicators': [
        'unemployment', 'gdp growth', 'consumer spending', 'housing market', 'oil prices'
    ],
    'sectors': [
        'tech stocks', 'banking stocks', 'energy stocks', 'healthcare stocks', 'crypto'
    ],
    'events': [
        'earnings season', 'fed meeting', 'jobs report', 'cpi report', 'market correction'
    ],
    'all': [
        'stock market crash', 'recession', 'inflation', 'bear market', 'bull market',
        'buy stocks', 'sell stocks', 'stock market news', 'market volatility', 'fed interest rates',
        'unemployment', 'gdp growth', 'consumer spending', 'housing market', 'oil prices',
        'tech stocks', 'banking stocks', 'energy stocks', 'healthcare stocks', 'crypto',
        'earnings season', 'fed meeting', 'jobs report', 'cpi report', 'market correction'
    ]
}

# ETL Configuration
ETL_CONFIG = {
    'price_data': {
        'periods': ['5d', '3mo', '1y'],
        'intervals': ['1h', '1d'],
        'batch_size': 10
    },
    'macro_data': {
        'lookback_days': 730,  # 2 years
        'batch_size': 5
    },
    'trends_data': {
        'timeframes': ['today 3-m', 'today 1-m', 'now 7-d'],
        'geo': 'US',
        'batch_size': 5
    },
    'news_data': {
        'lookback_hours': 24,
        'max_articles_per_symbol': 10,
        'batch_size': 5
    }
}

# Market Hours Configuration
MARKET_HOURS = {
    'timezone': 'US/Eastern',
    'open_time': '09:30',
    'close_time': '16:00',
    'trading_days': [0, 1, 2, 3, 4],  # Monday to Friday
    'holidays': [
        '2024-01-01',  # New Year's Day
        '2024-01-15',  # Martin Luther King Jr. Day
        '2024-02-19',  # Presidents' Day
        '2024-03-29',  # Good Friday
        '2024-05-27',  # Memorial Day
        '2024-06-19',  # Juneteenth
        '2024-07-04',  # Independence Day
        '2024-09-02',  # Labor Day
        '2024-11-28',  # Thanksgiving
        '2024-12-25',  # Christmas Day
    ]
}

# GitHub Actions Configuration
GITHUB_ACTIONS_CONFIG = {
    'schedule': {
        'intraday': '0,30 9-16 * * 1-5',  # Every 30 minutes during market hours
        'daily': '0 6 * * *',  # Daily at 6 AM ET
        'weekly': '0 8 * * 1'  # Weekly on Monday at 8 AM ET
    },
    'python_version': '3.11',
    'retention_days': 7
}

# Tableau Configuration
TABLEAU_CONFIG = {
    'refresh_intervals': {
        'intraday': 30,  # minutes
        'daily': 1440,  # minutes (24 hours)
        'weekly': 10080  # minutes (7 days)
    },
    'color_scheme': {
        'positive': '#00B050',
        'negative': '#FF0000',
        'neutral': '#0070C0',
        'warning': '#FFC000',
        'info': '#808080'
    },
    'dashboard_settings': {
        'default_time_range': 90,  # days
        'max_data_points': 10000,
        'cache_timeout': 300  # seconds
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_rotation': {
        'max_bytes': 10485760,  # 10MB
        'backup_count': 5
    },
    'log_files': {
        'etl': 'logs/etl.log',
        'errors': 'logs/errors.log',
        'performance': 'logs/performance.log'
    }
}

# Data Quality Configuration
DATA_QUALITY_CONFIG = {
    'price_data': {
        'required_columns': ['symbol', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume'],
        'max_null_percentage': 5,
        'min_price': 0.01,
        'max_price': 100000
    },
    'macro_data': {
        'required_columns': ['indicator_id', 'date', 'value'],
        'max_null_percentage': 10,
        'value_range': {
            'unemployment_rate': (0, 20),
            'inflation_rate': (-5, 20),
            'interest_rate': (0, 20)
        }
    },
    'trends_data': {
        'required_columns': ['keyword', 'date', 'score', 'geo'],
        'max_null_percentage': 15,
        'score_range': (0, 100)
    },
    'news_data': {
        'required_columns': ['symbol', 'fetched_at', 'title', 'vader_compound'],
        'max_null_percentage': 20,
        'sentiment_range': (-1, 1)
    }
}

# Alert Configuration
ALERT_CONFIG = {
    'price_alerts': {
        'large_moves': 0.05,  # 5% daily move
        'volume_spikes': 2.0,  # 2x average volume
        'volatility_spikes': 0.03  # 3% daily volatility
    },
    'macro_alerts': {
        'inflation_threshold': 0.03,  # 3% monthly inflation
        'unemployment_threshold': 0.05,  # 5% unemployment rate
        'rate_change_threshold': 0.25  # 25 basis point change
    },
    'sentiment_alerts': {
        'extreme_sentiment': 0.8,  # |sentiment| > 0.8
        'sentiment_divergence': 0.5  # Sentiment vs price divergence
    }
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'database': {
        'connection_pool_size': 10,
        'query_timeout': 30,
        'batch_size': 1000
    },
    'api': {
        'request_timeout': 30,
        'max_concurrent_requests': 5,
        'retry_delay': 2
    },
    'memory': {
        'max_dataframe_size': 1000000,  # rows
        'chunk_size': 10000
    }
}

def get_market_status():
    """
    Get current market status (Open/Closed)
    
    Returns:
        str: 'Open' or 'Closed'
    """
    now = datetime.now()
    
    # Check if it's a weekend
    if now.weekday() >= 5:
        return 'Closed'
    
    # Check if it's a holiday
    date_str = now.strftime('%Y-%m-%d')
    if date_str in MARKET_HOURS['holidays']:
        return 'Closed'
    
    # Check market hours (simplified - assumes ET timezone)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    if market_open <= now <= market_close:
        return 'Open'
    else:
        return 'Closed'

def get_data_retention_days():
    """
    Get data retention period in days
    
    Returns:
        int: Number of days to retain data
    """
    return {
        'price_data': 365 * 2,  # 2 years
        'macro_data': 365 * 5,  # 5 years
        'trends_data': 365,  # 1 year
        'news_data': 90  # 3 months
    }

def get_refresh_schedule():
    """
    Get refresh schedule based on market status
    
    Returns:
        dict: Refresh schedule configuration
    """
    market_status = get_market_status()
    
    if market_status == 'Open':
        return {
            'price_data': 30,  # minutes
            'macro_data': 1440,  # daily
            'trends_data': 1440,  # daily
            'news_data': 60  # hourly
        }
    else:
        return {
            'price_data': 1440,  # daily
            'macro_data': 1440,  # daily
            'trends_data': 10080,  # weekly
            'news_data': 1440  # daily
        }
