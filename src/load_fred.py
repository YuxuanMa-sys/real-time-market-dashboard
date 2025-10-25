"""
ETL script for loading macroeconomic data from FRED API
Fetches key economic indicators like CPI, unemployment, interest rates
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import logging
from fredapi import Fred
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_fred_data(fred_api_key, indicators, start_date=None):
    """
    Fetch macroeconomic data from FRED API
    
    Args:
        fred_api_key (str): FRED API key
        indicators (dict): Dictionary mapping indicator_id to description
        start_date (str): Start date for data (YYYY-MM-DD format)
    
    Returns:
        pd.DataFrame: Macro data with columns [indicator_id, date, value]
    """
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
    
    fred = Fred(api_key=fred_api_key)
    all_data = []
    
    for indicator_id, description in indicators.items():
        try:
            logger.info(f"Fetching {indicator_id}: {description}")
            
            # Fetch data from FRED
            data = fred.get_series(indicator_id, start=start_date)
            
            if data.empty:
                logger.warning(f"No data found for {indicator_id}")
                continue
            
            # Convert to DataFrame
            df = pd.DataFrame({
                'indicator_id': indicator_id,
                'date': data.index.date,
                'value': data.values
            })
            
            all_data.append(df)
            logger.info(f"✅ Successfully fetched {len(df)} records for {indicator_id}")
            
        except Exception as e:
            logger.error(f"❌ Error fetching data for {indicator_id}: {e}")
            continue
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def load_macro_to_db(df, engine):
    """
    Load macroeconomic data to PostgreSQL database using batch upsert
    
    Args:
        df (pd.DataFrame): Macro data
        engine: SQLAlchemy engine
    """
    if df.empty:
        logger.warning("No data to load")
        return
    
    try:
        # Use pandas to_sql with method='upsert' equivalent
        # First, we'll use a custom batch upsert approach
        with engine.connect() as conn:
            # Process in batches of 1000 records
            batch_size = 1000
            total_rows = len(df)
            
            for i in range(0, total_rows, batch_size):
                batch_df = df.iloc[i:i+batch_size]
                logger.info(f"Loading batch {i//batch_size + 1}/{(total_rows-1)//batch_size + 1} ({len(batch_df)} records)")
                
                # Use pandas to_sql for batch insert
                batch_df.to_sql('f_macro_temp', engine, if_exists='replace', index=False)
                
                # Use SQL to upsert from temp table
                upsert_sql = text("""
                    INSERT INTO f_macro (indicator_id, date, value)
                    SELECT indicator_id, date, value FROM f_macro_temp
                    ON CONFLICT (indicator_id, date) 
                    DO UPDATE SET 
                        value = EXCLUDED.value,
                        created_at = CURRENT_TIMESTAMP
                """)
                
                conn.execute(upsert_sql)
                
                # Drop temp table
                conn.execute(text("DROP TABLE IF EXISTS f_macro_temp"))
                conn.commit()
            
            logger.info(f"✅ Successfully loaded {len(df)} macro records to database")
            
    except Exception as e:
        logger.error(f"❌ Error loading data to database: {e}")
        raise

def main():
    """Main ETL function"""
    
    # Get API key and database connection
    fred_api_key = os.getenv('FRED_API_KEY')
    pg_dsn = os.getenv('PG_DSN')
    
    if not fred_api_key:
        raise ValueError("FRED_API_KEY environment variable not set")
    if not pg_dsn:
        raise ValueError("PG_DSN environment variable not set")
    
    engine = create_engine(pg_dsn)
    
    # Define key macroeconomic indicators
    indicators = {
        'CPIAUCSL': 'Consumer Price Index for All Urban Consumers: All Items',
        'UNRATE': 'Unemployment Rate',
        'FEDFUNDS': 'Federal Funds Effective Rate',
        'UMCSENT': 'University of Michigan: Consumer Sentiment',
        'DGS10': '10-Year Treasury Constant Maturity Rate',
        'DGS2': '2-Year Treasury Constant Maturity Rate',
        'DGS30': '30-Year Treasury Constant Maturity Rate',
        'GDP': 'Gross Domestic Product',
        'PAYEMS': 'All Employees, Total Nonfarm',
        'INDPRO': 'Industrial Production Index',
        'RSXFS': 'Advance Retail Sales: Retail Trade',  # Corrected indicator
        'HOUST': 'Housing Starts: Total: New Privately Owned Housing Units Started',  # Corrected indicator
        'DGORDER': 'Manufacturers New Orders: Durable Goods',  # Corrected indicator
        'TCU': 'Capacity Utilization: Total Industry',  # Corrected indicator
        'M2SL': 'M2 Money Stock',
        'TOTALSA': 'Total Vehicle Sales',
        'CSUSHPISA': 'S&P/Case-Shiller U.S. National Home Price Index',
        'RECPROUSM156N': 'Recession Probabilities',
        'T10Y2Y': '10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity',
        'T10Y3M': '10-Year Treasury Constant Maturity Minus 3-Month Treasury Constant Maturity'
    }
    
    logger.info("🚀 Starting macroeconomic data ETL process")
    
    try:
        # Fetch data for last 2 years
        start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
        macro_data = get_fred_data(fred_api_key, indicators, start_date)
        
        # Load to database
        load_macro_to_db(macro_data, engine)
        
        logger.info("✅ Macroeconomic data ETL completed successfully")
        
    except Exception as e:
        logger.error(f"❌ ETL process failed: {e}")
        raise

if __name__ == "__main__":
    main()
