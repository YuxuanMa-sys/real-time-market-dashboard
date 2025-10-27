"""
ETL script for loading stock price data using yfinance
Fetches intraday data for major indices and sector ETFs
"""

import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_price_data(symbols, period="1mo", interval="1d"):
    """
    Fetch price data for given symbols
    
    Args:
        symbols (list): List of stock symbols
        period (str): Time period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        pd.DataFrame: Price data with columns [symbol, date, open, high, low, close, adj_close, volume]
    """
    all_data = []
    
    for symbol in symbols:
        try:
            logger.info(f"Fetching data for {symbol}")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                continue
            
            # Reset index to get date as column
            data = data.reset_index()
            # Map ^VIX to VIX for database consistency
            db_symbol = 'VIX' if symbol == '^VIX' else symbol
            data['symbol'] = db_symbol
            
            # Rename columns to match database schema (handle different column names)
            column_mapping = {
                'Date': 'date',
                'Datetime': 'date',  # For intraday data
                'Open': 'open', 
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Adj Close': 'adj_close',
                'Volume': 'volume',
                'Dividends': 'dividends',
                'Stock Splits': 'stock_splits',
                'Capital Gains': 'capital_gains'
            }
            
            # Check which columns exist and rename them
            for old_name, new_name in column_mapping.items():
                if old_name in data.columns:
                    data = data.rename(columns={old_name: new_name})
            
            # Handle missing date column (use index if no date column)
            if 'date' not in data.columns and not data.empty:
                data['date'] = data.index
            
            # Handle missing adj_close column (use close if adj_close doesn't exist)
            if 'adj_close' not in data.columns and 'close' in data.columns:
                data['adj_close'] = data['close']
            
            # Select only required columns (only include columns that exist)
            required_columns = ['symbol', 'date']
            optional_columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume', 'dividends', 'stock_splits', 'capital_gains']
            
            for col in optional_columns:
                if col in data.columns:
                    required_columns.append(col)
            
            data = data[required_columns]
            
            all_data.append(data)
            logger.info(f"✅ Successfully fetched {len(data)} records for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error fetching data for {symbol}: {e}")
            continue
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def load_prices_to_db(df, engine):
    """
    Load price data to PostgreSQL database using upsert
    
    Args:
        df (pd.DataFrame): Price data
        engine: SQLAlchemy engine
    """
    if df.empty:
        logger.warning("No data to load")
        return
    
    try:
        # Use pandas to_sql with method='upsert' equivalent
        # First, we'll use a custom upsert approach
        with engine.connect() as conn:
            for _, row in df.iterrows():
                upsert_sql = text("""
                    INSERT INTO f_price_daily (symbol, date, open, high, low, close, adj_close, volume, dividends, stock_splits, capital_gains)
                    VALUES (:symbol, :date, :open, :high, :low, :close, :adj_close, :volume, :dividends, :stock_splits, :capital_gains)
                    ON CONFLICT (symbol, date) 
                    DO UPDATE SET 
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        adj_close = EXCLUDED.adj_close,
                        volume = EXCLUDED.volume,
                        dividends = EXCLUDED.dividends,
                        stock_splits = EXCLUDED.stock_splits,
                        capital_gains = EXCLUDED.capital_gains,
                        created_at = CURRENT_TIMESTAMP
                """)
                
                conn.execute(upsert_sql, {
                    'symbol': row['symbol'],
                    'date': row['date'].date(),
                    'open': float(row['open']) if pd.notna(row['open']) else None,
                    'high': float(row['high']) if pd.notna(row['high']) else None,
                    'low': float(row['low']) if pd.notna(row['low']) else None,
                    'close': float(row['close']) if pd.notna(row['close']) else None,
                    'adj_close': float(row['adj_close']) if pd.notna(row['adj_close']) else None,
                    'volume': int(row['volume']) if pd.notna(row['volume']) else None,
                    'dividends': float(row['dividends']) if pd.notna(row['dividends']) else None,
                    'stock_splits': float(row['stock_splits']) if pd.notna(row['stock_splits']) else None,
                    'capital_gains': float(row['capital_gains']) if pd.notna(row['capital_gains']) else None
                })
            
            conn.commit()
            logger.info(f"✅ Successfully loaded {len(df)} price records to database")
            
    except Exception as e:
        logger.error(f"❌ Error loading data to database: {e}")
        raise

def main():
    """Main ETL function"""
    
    # Get database connection
    pg_dsn = os.getenv('PG_DSN')
    if not pg_dsn:
        raise ValueError("PG_DSN environment variable not set")
    
    engine = create_engine(pg_dsn)
    
    # Define symbols to track
    symbols = [
        'SPY', 'QQQ', 'IWM', 'EFA', 'VTI',  # Broad market
        'XLF', 'XLK', 'XLE', 'XLI', 'XLV',  # Sector ETFs
        'XLY', 'XLP', 'XLU', 'XLB', 'XLRE', # More sectors
        '^VIX'  # Volatility index (use ^VIX instead of VIX)
    ]
    
    logger.info("🚀 Starting price data ETL process")
    
    try:
        # Fetch data for different time periods
        # Intraday data (last 5 days with 1-hour intervals)
        logger.info("Fetching intraday data...")
        intraday_data = get_price_data(symbols, period="5d", interval="1h")
        
        # Daily data (last 3 months)
        logger.info("Fetching daily data...")
        daily_data = get_price_data(symbols, period="3mo", interval="1d")
        
        # Combine and deduplicate
        all_data = pd.concat([intraday_data, daily_data], ignore_index=True)
        all_data = all_data.drop_duplicates(subset=['symbol', 'date'], keep='last')
        
        # Load to database
        load_prices_to_db(all_data, engine)
        
        logger.info("✅ Price data ETL completed successfully")
        
    except Exception as e:
        logger.error(f"❌ ETL process failed: {e}")
        raise

if __name__ == "__main__":
    main()
