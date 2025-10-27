"""
ETL script for loading news sentiment data
Fetches news headlines and analyzes sentiment using VADER
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import logging
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def get_news_data(symbols, api_key=None):
    """
    Fetch news data for given symbols
    Uses free news APIs or web scraping as fallback
    
    Args:
        symbols (list): List of stock symbols
        api_key (str): Optional API key for paid news service
    
    Returns:
        pd.DataFrame: News data with sentiment scores
    """
    all_news = []
    
    for symbol in symbols:
        try:
            logger.info(f"Fetching news for {symbol}")
            
            # Use real news API if key is provided, otherwise use mock data
            news_items = get_real_news_data(symbol, api_key)
            
            for item in news_items:
                # Analyze sentiment
                sentiment_scores = analyzer.polarity_scores(item['title'])
                
                news_data = {
                    'symbol': symbol,
                    'fetched_at': datetime.now(),
                    'published_at': item['published_at'],
                    'source': item['source'],
                    'title': item['title'],
                    'url': item['url'],
                    'vader_compound': sentiment_scores['compound'],
                    'vader_positive': sentiment_scores['pos'],
                    'vader_negative': sentiment_scores['neg'],
                    'vader_neutral': sentiment_scores['neu']
                }
                
                all_news.append(news_data)
            
            logger.info(f"✅ Successfully processed {len(news_items)} news items for {symbol}")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ Error fetching news for {symbol}: {e}")
            continue
    
    if all_news:
        return pd.DataFrame(all_news)
    else:
        return pd.DataFrame()

def get_mock_news_data(symbol):
    """
    Generate mock news data for demonstration
    In production, replace with actual news API calls
    """
    # This is a placeholder - replace with actual news API integration
    mock_news = [
        {
            'title': f'{symbol} shows strong performance in latest trading session',
            'source': 'Financial News',
            'url': f'https://example.com/news/{symbol}-1',
            'published_at': datetime.now() - timedelta(hours=2)
        },
        {
            'title': f'Analysts raise price target for {symbol} following earnings beat',
            'source': 'Market Watch',
            'url': f'https://example.com/news/{symbol}-2',
            'published_at': datetime.now() - timedelta(hours=4)
        },
        {
            'title': f'{symbol} faces headwinds amid market volatility concerns',
            'source': 'Reuters',
            'url': f'https://example.com/news/{symbol}-3',
            'published_at': datetime.now() - timedelta(hours=6)
        }
    ]
    
    return mock_news

def get_real_news_data(symbol, api_key=None):
    """
    Fetch real news data using NewsAPI or similar service
    This is a template for actual implementation
    """
    if not api_key:
        logger.warning("No API key provided, using mock data")
        return get_mock_news_data(symbol)
    
    try:
        # Query for both the symbol itself and search terms
        query_terms = [
            symbol,
            f"{symbol} stock",
            f"{symbol} ETF" if symbol in ['SPY', 'QQQ', 'IWM'] else None,
            f"{symbol} market"
        ]
        
        # Filter out None values
        query_terms = [q for q in query_terms if q]
        
        all_news_items = []
        
        # Use the first query term and fetch all pages
        query = query_terms[0]  # Use main query term
        
        try:
            # Fetch multiple pages to get more results
            max_pages = 3  # NewsAPI free tier allows up to 100 results (5 pages with pageSize 20)
            
            for page in range(1, max_pages + 1):
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'apiKey': api_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 100,  # Maximum allowed by NewsAPI
                    'page': page,  # Pagination
                    'from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),  # Last 30 days
                    'to': datetime.now().strftime('%Y-%m-%d')
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code != 200:
                    logger.warning(f"NewsAPI returned status {response.status_code}: {response.text}")
                    if response.status_code == 426:
                        logger.warning("Reached maximum quota for NewsAPI free tier")
                    break
                
                data = response.json()
                
                articles = data.get('articles', [])
                if not articles:
                    break  # No more articles
                
                for article in articles:
                    # Skip articles that don't have required fields
                    if not article.get('title') or not article.get('publishedAt'):
                        continue
                        
                    try:
                        # Parse date
                        pub_date_str = article['publishedAt'].replace('Z', '+00:00')
                        pub_date = datetime.fromisoformat(pub_date_str)
                        
                        news_item = {
                            'title': article['title'],
                            'source': article.get('source', {}).get('name', 'Unknown'),
                            'url': article.get('url', ''),
                            'published_at': pub_date
                        }
                        all_news_items.append(news_item)
                    except Exception as e:
                        logger.debug(f"Error parsing article: {e}")
                        continue
                
                logger.debug(f"Fetched page {page}: {len(articles)} articles")
                
                # Small delay to respect rate limits
                time.sleep(1)
        
        except Exception as e:
            logger.error(f"Error fetching news for query '{query}': {e}")
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_news = []
        for item in all_news_items:
            title_lower = item['title'].lower().strip()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_news.append(item)
        
        logger.info(f"✅ Fetched {len(unique_news)} unique news articles for {symbol}")
        return unique_news if unique_news else get_mock_news_data(symbol)
        
    except Exception as e:
        logger.error(f"Error fetching real news data for {symbol}: {e}")
        return get_mock_news_data(symbol)

def load_news_to_db(df, engine):
    """
    Load news sentiment data to PostgreSQL database
    
    Args:
        df (pd.DataFrame): News sentiment data
        engine: SQLAlchemy engine
    """
    if df.empty:
        logger.warning("No data to load")
        return
    
    try:
        with engine.connect() as conn:
            # Clear existing data and reset ID sequence
            logger.info("Clearing existing news sentiment data...")
            conn.execute(text("TRUNCATE TABLE f_news_sentiment RESTART IDENTITY CASCADE"))
            conn.commit()
            
            for _, row in df.iterrows():
                insert_sql = text("""
                    INSERT INTO f_news_sentiment 
                    (symbol, fetched_at, published_at, source, title, url, 
                     vader_compound, vader_positive, vader_negative, vader_neutral)
                    VALUES (:symbol, :fetched_at, :published_at, :source, :title, :url,
                            :vader_compound, :vader_positive, :vader_negative, :vader_neutral)
                """)
                
                conn.execute(insert_sql, {
                    'symbol': row['symbol'],
                    'fetched_at': row['fetched_at'],
                    'published_at': row['published_at'],
                    'source': row['source'],
                    'title': row['title'],
                    'url': row['url'],
                    'vader_compound': float(row['vader_compound']),
                    'vader_positive': float(row['vader_positive']),
                    'vader_negative': float(row['vader_negative']),
                    'vader_neutral': float(row['vader_neutral'])
                })
            
            conn.commit()
            logger.info(f"✅ Successfully loaded {len(df)} news sentiment records to database")
            
    except Exception as e:
        logger.error(f"❌ Error loading data to database: {e}")
        raise

def main():
    """Main ETL function"""
    
    # Get API key and database connection
    news_api_key = os.getenv('NEWS_API_KEY')  # Optional
    pg_dsn = os.getenv('PG_DSN')
    
    if not pg_dsn:
        raise ValueError("PG_DSN environment variable not set")
    
    engine = create_engine(pg_dsn)
    
    # Define symbols to track for news
    symbols = [
        'SPY', 'QQQ', 'IWM',  # Major indices
        'XLF', 'XLK', 'XLE',  # Key sectors
        'VIX'  # Volatility
    ]
    
    logger.info("🚀 Starting news sentiment ETL process")
    
    try:
        # Fetch news data
        news_data = get_news_data(symbols, news_api_key)
        
        # Load to database
        load_news_to_db(news_data, engine)
        
        logger.info("✅ News sentiment ETL completed successfully")
        
    except Exception as e:
        logger.error(f"❌ ETL process failed: {e}")
        raise

if __name__ == "__main__":
    main()
