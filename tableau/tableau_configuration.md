# Tableau Cloud Configuration Guide

## Database Connection Setup

### 1. Connect to Railway PostgreSQL

1. **Open Tableau Desktop/Cloud**
2. **Connect to Data** → **PostgreSQL**
3. **Enter Connection Details:**
   - Server: `[Your Railway PostgreSQL Host]`
   - Port: `5432`
   - Database: `[Your Database Name]`
   - Username: `[Your Username]`
   - Password: `[Your Password]`
   - SSL Mode: `Require`

### 2. Configure Live Connection

1. **Select "Live Connection"** (not Extract)
2. **Enable "Auto-refresh"** for real-time updates
3. **Set refresh interval** to 30 minutes during market hours

### 3. Data Source Configuration

#### Primary Data Sources:
- `f_price_daily` - Stock price data
- `f_macro` - Macroeconomic indicators  
- `f_trends` - Google Trends data
- `f_news_sentiment` - News sentiment scores
- `dim_symbol` - Symbol metadata
- `dim_indicator` - Indicator metadata

## Dashboard Design Guidelines

### Overview Tab
**Purpose:** Market snapshot and key metrics

**Key Visuals:**
- **Sector Heatmap:** Use `f_price_daily` with `dim_symbol.sector`
- **S&P 500 Trend:** Line chart of SPY close prices
- **VIX Gauge:** Current volatility level
- **Market Status:** Open/Closed indicator

**Calculations:**
```sql
-- Daily Return
{fixed [Symbol], [Date]: [Close] / lookup([Close], -1) - 1}

-- Sector Performance
{fixed [Sector], [Date]: avg([Close]) / avg(lookup([Close], -1)) - 1}

-- Volatility (20-day rolling)
{fixed [Symbol], [Date]: stdev([Daily Return], 20)}
```

### Sector Rotation Tab
**Purpose:** Compare sector momentum and performance

**Key Visuals:**
- **Performance Bars:** Sector ETFs by time window (1D, 1W, 1M, 3M)
- **Sparkline Matrix:** Mini charts for each sector
- **Relative Strength:** Sector vs S&P 500

**Calculations:**
```sql
-- Relative Performance vs SPY
{fixed [Symbol], [Date]: [Close] / lookup([Close], -20)} / 
{fixed [Symbol]: "SPY", [Date]: [Close] / lookup([Close], -20)}

-- Sector Momentum Score
{fixed [Sector], [Date]: avg([Daily Return]) * 252}
```

### Macro Lens Tab
**Purpose:** Economic pressure and macro indicators

**Key Visuals:**
- **CPI vs S&P Overlay:** Dual-axis chart
- **Yield Curve:** 2Y, 10Y, 30Y Treasury rates
- **Economic Calendar:** Upcoming releases

**Calculations:**
```sql
-- Inflation-Adjusted Returns
{fixed [Symbol], [Date]: [Close] / lookup([Close], -252)} / 
{fixed [Indicator]: "CPIAUCSL", [Date]: [Value] / lookup([Value], -12)}

-- Yield Curve Spread
{fixed [Indicator]: "DGS10", [Date]: [Value]} - 
{fixed [Indicator]: "DGS2", [Date]: [Value]}
```

### Trends & Sentiment Tab
**Purpose:** Market psychology and sentiment analysis

**Key Visuals:**
- **Google Trends Lines:** Search interest over time
- **Sentiment vs Price:** Scatter plot with trend line
- **Sentiment Divergence:** When sentiment doesn't match price action

**Calculations:**
```sql
-- Sentiment Score (7-day average)
{fixed [Symbol], [Date]: avg([Vader Compound])}

-- Sentiment-Price Divergence
{fixed [Symbol], [Date]: [Sentiment Score]} - 
{fixed [Symbol], [Date]: [Daily Return] * 10}

-- Trend Momentum
{fixed [Keyword], [Date]: [Score] / lookup([Score], -7) - 1}
```

### Volatility & Risk Tab
**Purpose:** Risk management and volatility analysis

**Key Visuals:**
- **Rolling Drawdown:** Maximum peak-to-trough decline
- **ATR/Vol Bands:** Average True Range volatility
- **Anomaly Alerts:** Unusual price movements

**Calculations:**
```sql
-- Rolling Maximum
{fixed [Symbol], [Date]: max([Close], -252)}

-- Drawdown
{fixed [Symbol], [Date]: [Close] / [Rolling Maximum] - 1}

-- Average True Range (14-day)
{fixed [Symbol], [Date]: avg(max([High] - [Low], abs([High] - lookup([Close], -1)), abs([Low] - lookup([Close], -1))), 14)}

-- Volatility Percentile
{fixed [Symbol], [Date]: percentile([Daily Return], 0.95)}
```

## Dashboard Layout Best Practices

### 1. Responsive Design
- Use containers for flexible layouts
- Set minimum/maximum sizes for key visuals
- Test on different screen sizes

### 2. Color Coding
- **Green:** Positive performance/growth
- **Red:** Negative performance/decline  
- **Blue:** Neutral/informational
- **Yellow:** Warning/caution
- **Gray:** Historical/inactive

### 3. Interactivity
- **Filters:** Date range, symbols, sectors
- **Parameters:** Time windows, thresholds
- **Actions:** Cross-filtering between sheets
- **Drill-down:** From sector to individual stocks

### 4. Performance Optimization
- **Use data source filters** to limit data volume
- **Implement incremental refresh** where possible
- **Cache frequently used calculations**
- **Optimize database queries** with proper indexing

## Auto-Refresh Configuration

### 1. Data Source Level
- Set refresh interval to 30 minutes
- Enable "Refresh on open"
- Use "Refresh on data change" if supported

### 2. Dashboard Level  
- Enable "Auto-refresh" toggle
- Set appropriate refresh intervals
- Consider user experience vs data freshness

### 3. Workbook Level
- Publish with "Refresh on open"
- Set up scheduled refreshes
- Monitor refresh performance

## Security Considerations

### 1. Data Access
- Use read-only database user
- Implement row-level security if needed
- Monitor data access logs

### 2. Credential Management
- Store credentials securely in Tableau Cloud
- Use embedded credentials
- Rotate passwords regularly

### 3. Sharing Controls
- Set appropriate permissions
- Use projects for organization
- Monitor user access

## Troubleshooting Common Issues

### 1. Connection Problems
- Verify Railway database is accessible
- Check SSL certificate validity
- Test connection with different tools

### 2. Performance Issues
- Monitor query execution times
- Check database indexes
- Optimize calculations

### 3. Data Quality
- Implement data validation rules
- Monitor for missing data
- Set up alerts for anomalies
