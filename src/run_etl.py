"""
Main ETL orchestrator script
Coordinates all data loading processes
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import ETL modules
from load_prices import main as load_prices_main
from load_fred import main as load_fred_main
from load_trends import main as load_trends_main
from load_news_sentiment import main as load_news_main

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_etl_pipeline():
    """Run the complete ETL pipeline"""
    
    logger.info("🚀 Starting Real-Time Market Dashboard ETL Pipeline")
    start_time = datetime.now()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    etl_modules = [
        ("Price Data", load_prices_main),
        ("Macroeconomic Data", load_fred_main),
        ("Google Trends", load_trends_main),
        ("News Sentiment", load_news_main)
    ]
    
    results = {}
    
    for module_name, module_func in etl_modules:
        try:
            logger.info(f"📊 Starting {module_name} ETL...")
            module_start = datetime.now()
            
            module_func()
            
            module_duration = datetime.now() - module_start
            results[module_name] = {
                'status': 'success',
                'duration': module_duration.total_seconds()
            }
            
            logger.info(f"✅ {module_name} ETL completed in {module_duration.total_seconds():.2f} seconds")
            
        except Exception as e:
            logger.error(f"❌ {module_name} ETL failed: {e}")
            results[module_name] = {
                'status': 'failed',
                'error': str(e)
            }
    
    # Summary
    total_duration = datetime.now() - start_time
    successful_modules = sum(1 for r in results.values() if r['status'] == 'success')
    total_modules = len(results)
    
    logger.info(f"📈 ETL Pipeline Summary:")
    logger.info(f"   Total Duration: {total_duration.total_seconds():.2f} seconds")
    logger.info(f"   Successful Modules: {successful_modules}/{total_modules}")
    
    for module_name, result in results.items():
        if result['status'] == 'success':
            logger.info(f"   ✅ {module_name}: {result['duration']:.2f}s")
        else:
            logger.info(f"   ❌ {module_name}: {result['error']}")
    
    return results

if __name__ == "__main__":
    run_etl_pipeline()
