# Bitcoin Trading Simulator

A Bitcoin historical data viewer and virtual trading simulator built with Streamlit. View historical BTC-USD price data and practice trading strategies with a virtual $10,000 portfolio.

## Features

### 📈 Historical Data Viewer
- **Interactive Charts**: Candlestick charts with 5-hour sliding windows
- **Multiple Timeframes**: 5m, 10m, 15m, 30m, and 1h intervals
- **Timezone Support**: Auto-detection with manual override options
- **Random Date Picker**: Explore random historical periods from the past 45 days

### 💰 Virtual Trading
- **$10,000 Starting Portfolio**: Begin with virtual cash to practice trading
- **Turn-Based Trading**: Execute buy, sell, or hold actions each turn
- **Real Price Data**: Trade using actual historical Bitcoin prices
- **Realistic Trading Fees**: 0.5% trading fee + $15-50 gas fees (scales with trade size)
- **Smart Memory**: Remembers your preferred trade amounts
- **Complete History**: Track all trades with detailed transaction records and fee breakdowns

### 🎮 User Experience
- **Dual Modes**: Switch between chart viewing and trading simulation
- **Auto-Refresh**: Charts update automatically when changing parameters
- **Compact Design**: Optimized layout for efficient screen usage
- **Persistent State**: Your trading session and preferences are maintained

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd tradr
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run bitcoin_trader_streamlit.py
```

## Usage

### Chart Viewing Mode
1. Select your preferred date, time, interval, and timezone
2. The chart automatically updates with historical Bitcoin data
3. Use the "🎲 Random" button to explore random historical periods
4. View 5 hours of price data ending at your selected time

### Trading Mode
1. Click "Enable Trading" to enter simulation mode
2. View your portfolio: Cash, BTC holdings, and total value
3. Select an action: Buy, Sell, or Hold
4. Enter your trade amount (see real-time fee estimates)
5. Review total costs (buy) or net proceeds (sell) including fees
6. Click "▶️ Next" to execute the trade and advance time
7. Monitor your trading history and portfolio performance with fee details

## Trading Features

- **Buy Orders**: Purchase BTC using your cash balance (plus trading and gas fees)
- **Sell Orders**: Convert BTC back to cash (minus trading and gas fees)
- **Hold Actions**: Skip trading but advance to the next time interval
- **Realistic Fee Structure**:
  - Trading fee: 0.5% of trade amount (taker fee)
  - Gas fee: $15-50 dynamically calculated based on trade size and network conditions
- **Trade Validation**: Prevents trades exceeding available balances (including fees)
- **Price Execution**: First turn uses close prices, subsequent turns use open prices
- **Fee Transparency**: Real-time fee estimates and detailed fee breakdowns in trade history
- **Comprehensive Logging**: All trades, holds, failures, and fee details are recorded

## Technical Details

- **Data Source**: Yahoo Finance API via `yfinance`
- **Charts**: Interactive Plotly candlestick charts
- **UI Framework**: Streamlit with session state management
- **Time Handling**: Automatic timezone detection and conversion
- **Data Range**: Past 45 days of historical Bitcoin data

## Dependencies

- streamlit
- yfinance
- plotly
- pandas
- numpy
- pytz
- datetime
- random
- logging

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is a virtual trading simulator for educational purposes only. It uses historical data and does not involve real money or actual cryptocurrency trading. Past performance does not guarantee future results. This tool should not be used as the sole basis for investment decisions.