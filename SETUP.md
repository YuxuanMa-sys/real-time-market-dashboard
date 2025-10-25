# Setup Guide for Real-Time Market Dashboard

## Prerequisites

Before setting up the dashboard, ensure you have:

1. **Python 3.11+** installed
2. **Git** for version control
3. **Railway account** for PostgreSQL hosting
4. **FRED API key** (free from St. Louis Fed)
5. **GitHub account** for Actions and repository hosting
6. **Tableau Cloud/Desktop** for visualization

## Step-by-Step Setup

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd real-time-market-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup (Railway)

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create PostgreSQL Database**
   - Click "New Project"
   - Select "Database" → "PostgreSQL"
   - Railway will provide connection details

3. **Get Connection String**
   - Copy the PostgreSQL connection string
   - Format: `postgresql://username:password@host:port/database`

### 3. Environment Configuration

1. **Create Environment File**
   ```bash
   cp env.example .env
   ```

2. **Edit .env File**
   ```env
   PG_DSN=postgresql://username:password@host:port/database
   FRED_API_KEY=your_fred_api_key_here
   NEWS_API_KEY=your_news_api_key_here  # Optional
   ```

3. **Get FRED API Key**
   - Go to [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)
   - Sign up for free account
   - Generate API key

### 4. Initialize Database

```bash
# Run database setup
python src/setup_database.py
```

This will create all necessary tables and insert default data.

### 5. Test ETL Pipeline

```bash
# Test individual ETL scripts
python src/load_prices.py
python src/load_fred.py
python src/load_trends.py
python src/load_news_sentiment.py

# Or run complete pipeline
python src/run_etl.py
```

### 6. GitHub Actions Setup

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial setup"
   git push origin main
   ```

2. **Configure Secrets**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `PG_DSN`: Your Railway PostgreSQL connection string
     - `FRED_API_KEY`: Your FRED API key
     - `NEWS_API_KEY`: Optional news API key

3. **Enable Actions**
   - Go to Actions tab in your repository
   - Enable GitHub Actions if prompted

### 7. Tableau Cloud Setup

1. **Connect to Database**
   - Open Tableau Desktop/Cloud
   - Connect to PostgreSQL
   - Use Railway connection details

2. **Configure Live Connection**
   - Select "Live Connection" (not Extract)
   - Enable "Auto-refresh"
   - Set refresh interval to 30 minutes

3. **Create Dashboards**
   - Follow the Tableau configuration guide in `tableau/tableau_configuration.md`
   - Use the provided calculations and visualizations

## Configuration Options

### ETL Scheduling

The GitHub Actions workflow runs:
- **Every 30 minutes** during US market hours (9:30 AM - 4:00 PM ET, Monday-Friday)
- **Daily at 6 AM ET** for full refresh
- **Manual triggers** for testing

### Data Sources

| Source | Frequency | Notes |
|--------|-----------|-------|
| Stock Prices | Intraday (30 min) | Major indices and sector ETFs |
| FRED Data | Daily/Monthly | Macroeconomic indicators |
| Google Trends | Daily/Weekly | Market sentiment keywords |
| News Sentiment | Continuous | VADER sentiment analysis |

### Customization

Edit `src/config.py` to customize:
- Symbols to track
- Macro indicators
- Trends keywords
- ETL schedules
- Alert thresholds

## Monitoring and Maintenance

### Logs

- ETL logs: `logs/etl.log`
- Error logs: `logs/errors.log`
- Performance logs: `logs/performance.log`

### Data Quality

The system includes automatic data validation:
- Missing data detection
- Range validation
- Consistency checks
- Freshness monitoring

### Alerts

Configure alerts for:
- Large price movements (>5%)
- Volume spikes (>2x average)
- Data quality issues
- ETL failures

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify Railway database is running
   - Check connection string format
   - Ensure SSL is enabled

2. **API Rate Limits**
   - FRED API: 120 requests/minute
   - Google Trends: Built-in delays
   - News API: Depends on provider

3. **Missing Data**
   - Check market hours
   - Verify API keys
   - Review error logs

4. **Tableau Connection Issues**
   - Test database connection
   - Check firewall settings
   - Verify credentials

### Performance Optimization

1. **Database**
   - Monitor query performance
   - Add indexes as needed
   - Regular maintenance

2. **ETL Pipeline**
   - Batch processing
   - Parallel execution
   - Error handling

3. **Tableau**
   - Use data source filters
   - Optimize calculations
   - Cache frequently used data

## Security Considerations

1. **API Keys**
   - Store in environment variables
   - Use GitHub Secrets
   - Rotate regularly

2. **Database**
   - Use read-only user
   - Enable SSL
   - Monitor access

3. **Data Privacy**
   - No personal data collected
   - Public market data only
   - Follow data retention policies

## Support and Resources

- **Documentation**: This repository
- **Issues**: GitHub Issues tab
- **FRED API**: [fred.stlouisfed.org](https://fred.stlouisfed.org)
- **Railway**: [railway.app](https://railway.app)
- **Tableau**: [tableau.com](https://tableau.com)

## Next Steps

1. **Customize Dashboards**: Modify Tableau visualizations
2. **Add Data Sources**: Integrate additional APIs
3. **Implement Alerts**: Set up notification systems
4. **Scale Infrastructure**: Consider cloud deployment
5. **Add Analytics**: Implement machine learning models
