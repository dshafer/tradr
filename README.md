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
- **Turn-Based Trading**: Execute buy, sell, hold, or limit order actions each turn
- **Limit Orders**: Place conditional orders that execute automatically when price targets are reached
- **Real Price Data**: Trade using actual historical Bitcoin prices
- **Realistic Trading Fees**: 0.5% taker fee (market orders) + 0.25% maker fee (limit orders) + $15-50 gas fees
- **Order Management**: View, cancel, and track active limit orders with automatic execution
- **Smart Memory**: Remembers your preferred trade amounts
- **Complete History**: Track all trades with detailed transaction records and comprehensive fee breakdowns

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
3. Select an action: Buy, Sell, Hold, Limit Buy, or Limit Sell
4. Enter your trade amount (see real-time fee estimates)
5. For limit orders: Set your target price and click "📋 Place Limit Order"
6. For market orders: Review total costs (buy) or net proceeds (sell) including fees
7. Click "▶️ Next" to execute market trades and advance time
8. Monitor active limit orders and cancel if needed
9. Track your trading history and portfolio performance with comprehensive fee details

## Trading Features

### Market Orders
- **Buy Orders**: Purchase BTC immediately using your cash balance (plus trading and gas fees)
- **Sell Orders**: Convert BTC back to cash immediately (minus trading and gas fees)
- **Hold Actions**: Skip trading but advance to the next time interval

### Limit Orders
- **Limit Buy Orders**: Set a target price below current market - executes automatically when price drops to/below target
- **Limit Sell Orders**: Set a target price above current market - executes automatically when price rises to/above target
- **Order Management**: View all active orders, cancel orders, automatic execution notifications
- **Price Validation**: Interface warns when limit prices don't make sense (buy limit above market, sell limit below market)

### Fee Structure
- **Market Orders**: 0.5% trading fee (taker fee) + $15-50 gas fee
- **Limit Orders**: 0.25% trading fee (maker fee) + $15-50 gas fee
- **Gas Fees**: $15-50 dynamically calculated based on trade size and simulated network conditions

### Execution & Validation
- **Trade Validation**: Prevents trades exceeding available balances (including fees)
- **Price Execution**: First turn uses close prices, subsequent turns use open prices
- **Automatic Execution**: Limit orders execute automatically when price conditions are met
- **Fee Transparency**: Real-time fee estimates and detailed fee breakdowns in trade history
- **Comprehensive Logging**: All trades, holds, failures, order placements, executions, and fee details are recorded

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