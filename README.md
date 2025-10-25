# Real-Time Market & Macro Intelligence Dashboard

A comprehensive dashboard that integrates stock prices, macroeconomic indicators, Google search trends, and news sentiment for real-time market analysis.

## Architecture

```
GitHub Actions (Scheduled ETL)
        ↓
Updates PostgreSQL on Railway (Live Hosted DB)
        ↓
Tableau Cloud (Live Connection to Railway)
        ↓
Dashboard Auto-Updates in Real Time
```

## Data Sources

| Category | Source | Frequency | Notes |
|----------|--------|-----------|-------|
| Stock Market Data | yfinance | Intraday (every 30 min) | Indices, sector ETFs, individual tickers |
| Macroeconomic Indicators | FRED API | Daily / Monthly | CPI, Unemployment, Fed Funds Rate, Consumer Sentiment |
| Consumer Search Trends | Google Trends (pytrends) | Daily / Weekly | Interest signals & momentum indicators |
| News Sentiment | Ticker News + VADER | Continuous | Converts news headlines into sentiment scores |

## Database Schema

### Dimension Tables
- `dim_symbol(symbol, name, sector)`
- `dim_indicator(indicator_id, name, frequency)`

### Fact Tables
- `f_price_daily(symbol, date, open, high, low, close, adj_close, volume)`
- `f_macro(indicator_id, date, value)`
- `f_trends(keyword, date, score, geo)`
- `f_news_sentiment(symbol, fetched_at, published_at, source, title, url, vader_compound)`

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file with:
   ```
   PG_DSN=postgresql://username:password@host:port/database
   FRED_API_KEY=your_fred_api_key
   ```

3. **Database Setup**
   Run the database schema creation:
   ```bash
   python src/setup_database.py
   ```

4. **GitHub Actions Setup**
   - Add secrets to your GitHub repository:
     - `PG_DSN`: PostgreSQL connection string
     - `FRED_API_KEY`: FRED API key
   - Enable GitHub Actions in your repository

5. **Tableau Cloud Configuration**
   - Connect to Railway PostgreSQL using Live Connection
   - Embed credentials
   - Enable Auto-Refresh for real-time updates

## Dashboard Tabs

| Tab | Purpose | Key Visuals |
|-----|---------|-------------|
| Overview | Market snapshot | Sector heatmap, S&P trend, VIX gauge |
| Sector Rotation | Compare sector momentum | Bar performance by time window, Sparkline matrix |
| Macro Lens | Show economic pressure | CPI vs S&P overlay, Yield curve spread indicator |
| Trends & Sentiment | Explain market psychology | Google Trends lines, Sentiment vs price divergence |
| Volatility & Risk | Identify instability | Rolling drawdown, ATR/vol bands, anomaly alerts |

## Key Insights

- How CPI or unemployment changes affect sector performance
- Which sectors lead/lag during macro stress periods
- How sentiment divergences can predict trend reversals
- When volatility spikes signal market regime shifts
