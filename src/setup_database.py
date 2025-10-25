"""
Database schema setup for Real-Time Market Dashboard
Creates all necessary tables for the data warehouse
"""

import os
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database_schema():
    """Create the complete database schema"""
    
    # Get database connection string
    pg_dsn = os.getenv('PG_DSN')
    if not pg_dsn:
        raise ValueError("PG_DSN environment variable not set")
    
    # Create SQLAlchemy engine
    engine = create_engine(pg_dsn)
    
    # Schema creation SQL
    schema_sql = """
    -- Dimension Tables
    
    -- Symbols dimension
    CREATE TABLE IF NOT EXISTS dim_symbol (
        symbol VARCHAR(20) PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        sector VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Indicators dimension
    CREATE TABLE IF NOT EXISTS dim_indicator (
        indicator_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        frequency VARCHAR(20),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Fact Tables
    
    -- Daily price data
    CREATE TABLE IF NOT EXISTS f_price_daily (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(20) REFERENCES dim_symbol(symbol),
        date DATE NOT NULL,
        open DECIMAL(12,4),
        high DECIMAL(12,4),
        low DECIMAL(12,4),
        close DECIMAL(12,4),
        adj_close DECIMAL(12,4),
        volume BIGINT,
        dividends DECIMAL(12,4),
        stock_splits DECIMAL(12,4),
        capital_gains DECIMAL(12,4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(symbol, date)
    );
    
    -- Macroeconomic indicators
    CREATE TABLE IF NOT EXISTS f_macro (
        id SERIAL PRIMARY KEY,
        indicator_id VARCHAR(50) REFERENCES dim_indicator(indicator_id),
        date DATE NOT NULL,
        value DECIMAL(15,6),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(indicator_id, date)
    );
    
    -- Google Trends data
    CREATE TABLE IF NOT EXISTS f_trends (
        id SERIAL PRIMARY KEY,
        keyword VARCHAR(100) NOT NULL,
        date DATE NOT NULL,
        score INTEGER,
        geo VARCHAR(10) DEFAULT 'US',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(keyword, date, geo)
    );
    
    -- News sentiment data
    CREATE TABLE IF NOT EXISTS f_news_sentiment (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(20) REFERENCES dim_symbol(symbol),
        fetched_at TIMESTAMP NOT NULL,
        published_at TIMESTAMP,
        source VARCHAR(100),
        title TEXT,
        url TEXT,
        vader_compound DECIMAL(5,4),
        vader_positive DECIMAL(5,4),
        vader_negative DECIMAL(5,4),
        vader_neutral DECIMAL(5,4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_price_daily_symbol_date ON f_price_daily(symbol, date);
    CREATE INDEX IF NOT EXISTS idx_price_daily_date ON f_price_daily(date);
    CREATE INDEX IF NOT EXISTS idx_macro_indicator_date ON f_macro(indicator_id, date);
    CREATE INDEX IF NOT EXISTS idx_macro_date ON f_macro(date);
    CREATE INDEX IF NOT EXISTS idx_trends_keyword_date ON f_trends(keyword, date);
    CREATE INDEX IF NOT EXISTS idx_news_sentiment_symbol ON f_news_sentiment(symbol);
    CREATE INDEX IF NOT EXISTS idx_news_sentiment_fetched_at ON f_news_sentiment(fetched_at);
    
    -- Insert default symbols (all symbols used in ETL scripts)
    INSERT INTO dim_symbol (symbol, name, sector) VALUES
    ('SPY', 'SPDR S&P 500 ETF Trust', 'Broad Market'),
    ('QQQ', 'Invesco QQQ Trust', 'Technology'),
    ('IWM', 'iShares Russell 2000 ETF', 'Small Cap'),
    ('EFA', 'iShares MSCI EAFE ETF', 'International'),
    ('VTI', 'Vanguard Total Stock Market ETF', 'Broad Market'),
    ('XLF', 'Financial Select Sector SPDR Fund', 'Financials'),
    ('XLK', 'Technology Select Sector SPDR Fund', 'Technology'),
    ('XLE', 'Energy Select Sector SPDR Fund', 'Energy'),
    ('XLI', 'Industrial Select Sector SPDR Fund', 'Industrials'),
    ('XLV', 'Health Care Select Sector SPDR Fund', 'Health Care'),
    ('XLY', 'Consumer Discretionary Select Sector SPDR Fund', 'Consumer Discretionary'),
    ('XLP', 'Consumer Staples Select Sector SPDR Fund', 'Consumer Staples'),
    ('XLU', 'Utilities Select Sector SPDR Fund', 'Utilities'),
    ('XLB', 'Materials Select Sector SPDR Fund', 'Materials'),
    ('XLRE', 'Real Estate Select Sector SPDR Fund', 'Real Estate'),
    ('^VIX', 'CBOE Volatility Index', 'Volatility'),
    ('VIX', 'CBOE Volatility Index', 'Volatility')  -- For news sentiment script
    ON CONFLICT (symbol) DO NOTHING;
    
    -- Insert default indicators (all indicators used in FRED ETL script)
    INSERT INTO dim_indicator (indicator_id, name, frequency, description) VALUES
    ('CPIAUCSL', 'Consumer Price Index for All Urban Consumers: All Items', 'Monthly', 'Inflation measure'),
    ('UNRATE', 'Unemployment Rate', 'Monthly', 'Labor market indicator'),
    ('FEDFUNDS', 'Federal Funds Effective Rate', 'Daily', 'Monetary policy rate'),
    ('UMCSENT', 'University of Michigan: Consumer Sentiment', 'Monthly', 'Consumer confidence'),
    ('DGS10', '10-Year Treasury Constant Maturity Rate', 'Daily', 'Long-term interest rate'),
    ('DGS2', '2-Year Treasury Constant Maturity Rate', 'Daily', 'Short-term interest rate'),
    ('DGS30', '30-Year Treasury Constant Maturity Rate', 'Daily', 'Long-term mortgage rate'),
    ('GDP', 'Gross Domestic Product', 'Quarterly', 'Economic growth measure'),
    ('PAYEMS', 'All Employees, Total Nonfarm', 'Monthly', 'Employment level'),
    ('INDPRO', 'Industrial Production Index', 'Monthly', 'Manufacturing activity'),
    ('RSXFS', 'Advance Retail Sales: Retail Trade', 'Monthly', 'Consumer spending indicator'),
    ('HOUST', 'Housing Starts: Total: New Privately Owned Housing Units Started', 'Monthly', 'Housing market indicator'),
    ('DGORDER', 'Manufacturers New Orders: Durable Goods', 'Monthly', 'Manufacturing orders'),
    ('TCU', 'Capacity Utilization: Total Industry', 'Monthly', 'Industrial capacity utilization'),
    ('M2SL', 'M2 Money Stock', 'Monthly', 'Money supply measure'),
    ('TOTALSA', 'Total Vehicle Sales', 'Monthly', 'Auto industry indicator'),
    ('CSUSHPISA', 'S&P/Case-Shiller U.S. National Home Price Index', 'Monthly', 'Home price index'),
    ('RECPROUSM156N', 'Recession Probabilities', 'Monthly', 'Recession probability model'),
    ('T10Y2Y', '10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity', 'Daily', 'Yield curve spread'),
    ('T10Y3M', '10-Year Treasury Constant Maturity Minus 3-Month Treasury Constant Maturity', 'Daily', 'Yield curve spread')
    ON CONFLICT (indicator_id) DO NOTHING;
    """
    
    try:
        with engine.connect() as conn:
            # Execute schema creation
            conn.execute(text(schema_sql))
            conn.commit()
            print("✅ Database schema created successfully!")
            
            # Verify tables were created
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            print(f"📊 Created tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        raise

if __name__ == "__main__":
    create_database_schema()
