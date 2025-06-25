# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Bitcoin Historical Data Viewer and Virtual Trading Simulator built with Streamlit. The application allows users to view 5 hours of historical BTC-USD price data from Yahoo Finance and simulate turn-based trading with a virtual $10,000 portfolio.

## Commands

### Running the Application
```bash
streamlit run bitcoin_trader_streamlit.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Single-File Application
- **bitcoin_trader_streamlit.py**: Main application file containing all functionality
  - Streamlit web interface with compact controls layout
  - Yahoo Finance API integration via yfinance
  - Plotly candlestick chart visualization with dynamic titles
  - Turn-based virtual trading system
  - Comprehensive logging to bitcoin_trader_streamlit.log

### Key Features
- **Dual Modes**: Chart viewing with auto-refresh OR turn-based trading mode
- **Virtual Trading**: $10,000 starting portfolio with buy/sell/hold actions
- **Turn Progression**: Manual time advancement with sliding 5-hour data window
- **Trade Memory**: Remembers last buy ($1,000 default) and sell amounts
- **Random Date Selection**: Pick random date/time within past 45 days
- **Multiple Time Intervals**: 5m, 10m, 15m, 30m, 1h data intervals
- **Timezone Management**: Auto-detection with manual override options
- **Persistent Trade History**: Complete record of all trading actions

### Key Components
- **Data Fetching**: Uses yfinance with configurable intervals and sliding window logic
- **Trading Engine**: Turn-based execution with first/subsequent turn handling
- **Portfolio Management**: Real-time balance calculations and validation
- **Time Management**: Auto-detects user timezone with manual progression in trading mode
- **Visualization**: Plotly candlestick charts with turn-specific titles
- **Session State**: Maintains trading state, balances, history, and preferences

### Trading System
- **Portfolio**: Starts with $10,000 cash, 0 BTC
- **Actions**: Buy (uses cash), Sell (converts BTC), Hold (no action)
- **Pricing**: First turn uses close price, subsequent turns use open price of new intervals
- **Validation**: Prevents insufficient balance trades, records failures
- **History**: Persistent log of all trades with color-coded success/failure indicators

### Data Flow

#### Normal Mode:
1. User selects date/time/interval/timezone (or uses random picker)
2. Auto-refresh triggers on any input change (unless trading mode enabled)
3. Application converts local time to UTC for Yahoo Finance API
4. Displays 5 hours of data ending at selected time

#### Trading Mode:
1. User enables trading mode (disables auto-refresh)
2. Selects action (buy/sell/hold) and amount
3. Clicks "Next Turn" to execute trade and advance time
4. New interval data fetched, chart slides forward one interval
5. Trade executes at new interval's price, balances update
6. Chart title updates to show current time window

### UI Layout
- **Compact Design**: 5-column control layout with inline status
- **Split View**: Chart (3.5 width) | Trading Panel (1.5 width)
- **Trading Panel**: Portfolio metrics, action controls, persistent history
- **Smart Inputs**: Remember user preferences, validate against available funds

### Session State Management
Critical state variables:
- `trading_mode`: Boolean for mode switching
- `cash_balance`, `btc_balance`: Portfolio values
- `current_price`: Latest BTC price for calculations
- `turn_number`: Current turn counter
- `trading_history`: Persistent list of all actions
- `last_buy_amount`, `last_sell_amount`: User preference memory
- `current_data_end_time`: Sliding window position for turn progression
- `cached_chart_data`: Preserves chart when toggling trading mode

## Dependencies
Core libraries: streamlit, yfinance, plotly, pandas, pytz, random
See requirements.txt for complete list.