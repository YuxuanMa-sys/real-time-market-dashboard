"""
ETL script for loading Google Trends data using pytrends
Fetches search interest trends for market-related keywords
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import logging
from pytrends.request import TrendReq
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_trends_data(keywords, geo='US', timeframe='today 3-m'):
    """
    Fetch Google Trends data for given keywords
    
    Args:
        keywords (list): List of keywords to search
        geo (str): Geographic region (US, GB, etc.)
        timeframe (str): Time period for trends data
    
    Returns:
        pd.DataFrame: Trends data with columns [keyword, date, score, geo]
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    all_data = []
    
    # Process keywords in batches to avoid rate limits
    batch_size = 5
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i+batch_size]
        
        try:
            logger.info(f"Fetching trends for batch: {batch}")
            
            # Build payload
            pytrends.build_payload(batch, cat=0, timeframe=timeframe, geo=geo, gprop='')
            
            # Get interest over time
            interest_df = pytrends.interest_over_time()
            
            if interest_df.empty:
                logger.warning(f"No trends data found for batch: {batch}")
                continue
            
            # Process each keyword
            for keyword in batch:
                if keyword in interest_df.columns:
                    keyword_data = pd.DataFrame({
                        'keyword': keyword,
                        'date': interest_df.index.date,
                        'score': interest_df[keyword].values,
                        'geo': geo
                    })
                    
                    all_data.append(keyword_data)
                    logger.info(f"✅ Successfully fetched {len(keyword_data)} records for {keyword}")
                else:
                    logger.warning(f"Keyword {keyword} not found in trends data")
            
            # Rate limiting
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ Error fetching trends for batch {batch}: {e}")
            continue
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def load_trends_to_db(df, engine):
    """
    Load trends data to PostgreSQL database using upsert
    
    Args:
        df (pd.DataFrame): Trends data
        engine: SQLAlchemy engine
    """
    if df.empty:
        logger.warning("No data to load")
        return
    
    try:
        with engine.connect() as conn:
            for _, row in df.iterrows():
                upsert_sql = text("""
                    INSERT INTO f_trends (keyword, date, score, geo)
                    VALUES (:keyword, :date, :score, :geo)
                    ON CONFLICT (keyword, date, geo) 
                    DO UPDATE SET 
                        score = EXCLUDED.score,
                        created_at = CURRENT_TIMESTAMP
                """)
                
                conn.execute(upsert_sql, {
                    'keyword': row['keyword'],
                    'date': row['date'],
                    'score': int(row['score']) if pd.notna(row['score']) else None,
                    'geo': row['geo']
                })
            
            conn.commit()
            logger.info(f"✅ Successfully loaded {len(df)} trends records to database")
            
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
    
    # Define market-related keywords to track
    keywords = [
        # Market sentiment
        'stock market crash',
        'recession',
        'inflation',
        'bear market',
        'bull market',
        
        # Investment terms
        'buy stocks',
        'sell stocks',
        'stock market news',
        'market volatility',
        'fed interest rates',
        
        # Economic indicators
        'unemployment',
        'gdp growth',
        'consumer spending',
        'housing market',
        'oil prices',
        
        # Sector-specific
        'tech stocks',
        'banking stocks',
        'energy stocks',
        'healthcare stocks',
        'crypto',
        
        # Market events
        'earnings season',
        'fed meeting',
        'jobs report',
        'cpi report',
        'market correction'
    ]
    
    logger.info("🚀 Starting Google Trends ETL process")
    
    try:
        # Fetch trends data for different timeframes
        timeframes = [
            'today 3-m',  # Last 3 months
            'today 1-m',  # Last month
            'now 7-d'     # Last 7 days
        ]
        
        all_trends_data = []
        
        for timeframe in timeframes:
            logger.info(f"Fetching trends for timeframe: {timeframe}")
            trends_data = get_trends_data(keywords, geo='US', timeframe=timeframe)
            
            if not trends_data.empty:
                all_trends_data.append(trends_data)
            
            # Rate limiting between timeframes
            time.sleep(5)
        
        # Combine all data
        if all_trends_data:
            combined_data = pd.concat(all_trends_data, ignore_index=True)
            # Remove duplicates, keeping the most recent data
            combined_data = combined_data.drop_duplicates(subset=['keyword', 'date', 'geo'], keep='last')
            
            # Load to database
            load_trends_to_db(combined_data, engine)
        
        logger.info("✅ Google Trends ETL completed successfully")
        
    except Exception as e:
        logger.error(f"❌ ETL process failed: {e}")
        raise

if __name__ == "__main__":
    main()
