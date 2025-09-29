# IQ Option API Integration Guide

## 🚀 Overview

The IQ Option Trading Bot now includes full integration with the real IQ Option API, enabling:

- ✅ **Real-time market data** from IQ Option servers
- ✅ **Actual trade execution** on IQ Option platform  
- ✅ **Account management** (balance, profile, history)
- ✅ **Market status monitoring** (open/closed markets)
- ✅ **Demo/Practice mode** for safe testing
- ✅ **Graceful fallback** to mock mode when API unavailable

## 📋 Prerequisites

### 1. IQ Option Account
- Active IQ Option account with verified email
- Username/email and password for API access
- Recommended: Start with demo/practice account

### 2. Python Dependencies
```bash
pip install iqoptionapi==4.3.0
```
Or run our setup script: `python setup.py`

### 3. Environment Configuration
Copy `.env.example` to `.env` and configure:

```bash
# Your actual IQ Option credentials
IQ_OPTION_EMAIL=your_email@example.com
IQ_OPTION_PASSWORD=your_actual_password

# Other settings...
```

## ⚡ Quick Start

### 1. Automated Setup
```bash
cd services/trading-bot
python setup.py
```

This script will:
- Check Python version compatibility
- Install all dependencies
- Set up environment files
- Run integration tests
- Provide next steps

### 2. Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Test integration
python test_iq_option_integration.py

# 4. Start API server
python -m uvicorn src.api.main:app --reload
```

## 🔒 Safety Configuration

**CRITICAL**: Always start with demo mode enabled!

### settings.yml Safety Settings:
```yaml
iq_option:
  demo_mode: true  # ALWAYS start with true!
  api_timeout: 30
  max_trade_amount: 100.0
  max_concurrent_trades: 3
  connection_retry_attempts: 3
```

### Trading Safety Limits:
```yaml
trading:
  max_daily_trades: 5
  stop_after_losses: 1
  trade_amount_ratio: 0.1  # Only 10% of balance per trade
  win_amount_multiplier: 1.7
```

## 🎯 API Endpoints

### Account Management
```bash
# Get account status
GET /api/v1/chart/iq-option/status

# Get profile information
GET /api/v1/chart/iq-option/profile

# Get current balance
GET /api/v1/chart/iq-option/balance

# Manual connect/disconnect
POST /api/v1/chart/iq-option/connect
POST /api/v1/chart/iq-option/disconnect
```

### Market Data
```bash
# Get real-time chart data
GET /api/v1/chart/data/EURUSD/M5?count=100

# Check market status
GET /api/v1/chart/market/EURUSD/status

# Get real-time quote
GET /api/v1/chart/market/EURUSD/quote

# Get multiple assets data
GET /api/v1/chart/data/multiple?assets=EURUSD,GBPUSD&timeframes=M1,M5
```

### Trading Operations
```bash
# Execute trade (BE CAREFUL!)
POST /api/v1/chart/trade/execute
{
  "asset": "EURUSD",
  "direction": "call",  # or "put"
  "amount": 10.0,
  "duration": 60
}

# Get trade history
GET /api/v1/chart/trade/history
```

### Trading Agent Control
```bash
# Start automated trading
POST /api/v1/chart/agent/start

# Stop trading
POST /api/v1/chart/agent/stop

# Get agent status
GET /api/v1/chart/agent/status
```

## 🧪 Testing

### Run All Integration Tests
```bash
python test_iq_option_integration.py
```

### Test Specific Components
```bash
# Test basic features (mock mode)
python test_new_features.py

# Test with real API (requires credentials)
python test_iq_option_integration.py

# Interactive demo
python demo.py
```

## 🔧 Configuration Options

### IQ Option Settings
```yaml
iq_option:
  demo_mode: true           # Use practice account
  api_timeout: 30          # Connection timeout
  max_trade_amount: 100.0  # Safety limit
  max_concurrent_trades: 3  # Simultaneous trades
```

### Supported Assets
The system supports 36+ assets including:

- **Forex**: EURUSD, GBPUSD, USDJPY, USDCHF, etc.
- **Crypto**: BTCUSD, ETHUSD, LTCUSD, XRPUSD, etc.
- **Stocks**: GOOGL, AAPL, MSFT, AMZN, TSLA, etc.
- **Commodities**: GOLD, SILVER, OIL, GAS
- **Indices**: SPX500, NDQ100, DAX30, FTSE100, etc.

### Supported Timeframes
- **M1** - 1 minute
- **M5** - 5 minutes
- **M15** - 15 minutes
- **M30** - 30 minutes
- **H1** - 1 hour
- **H4** - 4 hours
- **D1** - 1 day

## 🚦 Usage Modes

### 1. Mock Mode (Default)
- No real API connection required
- Uses simulated data and trades
- Perfect for development and testing
- Zero risk

### 2. Demo Mode (Real API + Practice Account)
- Real IQ Option API connection
- Uses practice/demo account
- Real market data, simulated trades
- No real money at risk

### 3. Live Mode (Real API + Real Account)
- Real IQ Option API connection
- Uses real trading account
- **REAL MONEY AT RISK**
- Only use after thorough testing

## 🛡️ Safety Features

### Built-in Protections
- ✅ **Demo mode by default**
- ✅ **Trade amount limits**
- ✅ **Daily trade limits**
- ✅ **Loss stop limits**
- ✅ **Market hours enforcement**
- ✅ **Connection error handling**
- ✅ **Graceful API fallback**

### Risk Management
- **Position sizing**: Configurable % of balance
- **Stop losses**: Automatic daily loss limits
- **Trade frequency**: Maximum trades per day
- **Market validation**: Only trade when markets open
- **Connection monitoring**: Automatic reconnection

## 🐛 Troubleshooting

### Common Issues

#### 1. "IQ Option API library not available"
```bash
# Install the required library
pip install iqoptionapi==4.3.0

# Or use our setup script
python setup.py
```

#### 2. "Failed to connect to IQ Option API"
- Check your email/password in `.env`
- Ensure your IQ Option account is active
- Check internet connection
- Verify IQ Option servers are operational

#### 3. "No data available for asset"
- Check if asset is supported
- Verify market is open for trading
- Try a different timeframe

#### 4. "Trade execution failed"
- Ensure sufficient account balance
- Check if market is open
- Verify trade parameters (amount, duration)
- Confirm demo mode for testing

### Debug Mode
Enable debug logging in `settings.yml`:
```yaml
logging:
  level: "DEBUG"
```

## 📊 Monitoring & Analytics

### Real-time Monitoring
```python
# Get live account status
response = requests.get("http://localhost:8000/api/v1/chart/iq-option/status")
print(response.json())

# Monitor trading agent
response = requests.get("http://localhost:8000/api/v1/chart/agent/status")
print(response.json())
```

### Performance Tracking
- Account balance changes
- Trade win/loss ratios
- Daily/weekly performance
- Risk metrics
- Asset performance

## 🚀 Production Deployment

### Recommended Steps
1. **Thorough testing in demo mode**
2. **Configure appropriate risk limits**
3. **Set up monitoring and alerts**
4. **Start with small amounts**
5. **Monitor closely**
6. **Scale gradually**

### Environment Setup
```bash
# Production environment variables
IQ_OPTION_EMAIL=your_production_email
IQ_OPTION_PASSWORD=your_secure_password
LOG_LEVEL=INFO
DEBUG=false
```

### Security Considerations
- **Never commit credentials to code**
- **Use environment variables**
- **Secure your .env file**
- **Monitor API access logs**
- **Use strong passwords**
- **Enable 2FA on IQ Option account**

## 📚 Additional Resources

### API Documentation
- Start server: `python -m uvicorn src.api.main:app --reload`
- Access docs: http://localhost:8000/api/v1/docs
- Interactive API testing available

### Code Examples
- **demo.py** - Interactive feature demonstration
- **test_*.py** - Comprehensive test suites
- **IMPLEMENTATION_SUMMARY.md** - Technical details

### Support & Community
- Review logs for error details
- Check IQ Option server status
- Verify account permissions
- Test with minimal amounts first

---

## ⚠️ FINAL SAFETY REMINDER

**This system can execute real trades with real money. Always:**

1. **Start with demo_mode: true**
2. **Test thoroughly before live trading**
3. **Use appropriate risk limits**
4. **Monitor trades closely**
5. **Never risk more than you can afford to lose**

**Trading carries significant financial risk. Use at your own discretion.**