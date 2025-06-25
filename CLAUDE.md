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
- **Limit Orders**: Place buy/sell orders that execute automatically when price conditions are met
- **Realistic Trading Fees**: 0.5% taker fee (market orders) + 0.25% maker fee (limit orders) + $15-50 gas fees
- **Turn Progression**: Manual time advancement with sliding 5-hour data window
- **Trade Memory**: Remembers last buy ($1,000 default) and sell amounts
- **Random Date Selection**: Pick random date/time within past 45 days
- **Multiple Time Intervals**: 5m, 10m, 15m, 30m, 1h data intervals
- **Timezone Management**: Auto-detection with manual override options
- **Persistent Trade History**: Complete record of all trading actions with fee details

### Key Components
- **Data Fetching**: Uses yfinance with configurable intervals and sliding window logic
- **Trading Engine**: Turn-based execution with first/subsequent turn handling
- **Limit Order Engine**: Automatic execution of pending orders when price conditions are met
- **Fee Calculator**: Realistic trading fees (0.5% taker, 0.25% maker) + dynamic gas fees ($15-50)
- **Portfolio Management**: Real-time balance calculations with fee validation
- **Time Management**: Auto-detects user timezone with manual progression in trading mode
- **Visualization**: Plotly candlestick charts with turn-specific titles
- **Session State**: Maintains trading state, balances, history, active orders, and preferences

### Trading System
- **Portfolio**: Starts with $10,000 cash, 0 BTC
- **Market Actions**: Buy (uses cash + fees), Sell (receives proceeds - fees), Hold (no action)
- **Limit Orders**: Limit Buy (execute when price drops to/below target), Limit Sell (execute when price rises to/above target)
- **Fees Structure**: 
  - Market orders: 0.5% trading fee (taker fee) + $15-50 gas fee
  - Limit orders: 0.25% trading fee (maker fee) + $15-50 gas fee
  - Gas fee: $15-50 dynamically calculated based on trade size and randomness
  - Buy trades: Total cost = trade amount + trading fee + gas fee
  - Sell trades: Net proceeds = trade amount - trading fee - gas fee
- **Pricing**: First turn uses close price, subsequent turns use open price of new intervals
- **Order Management**: View active limit orders, cancel orders, automatic execution when conditions are met
- **Validation**: Prevents insufficient balance trades (including fees), records failures
- **History**: Persistent log of all trades with color-coded success/failure indicators and comprehensive fee breakdown

### Data Flow

#### Normal Mode:
1. User selects date/time/interval/timezone (or uses random picker)
2. Auto-refresh triggers on any input change (unless trading mode enabled)
3. Application converts local time to UTC for Yahoo Finance API
4. Displays 5 hours of data ending at selected time

#### Trading Mode:
1. User enables trading mode (disables auto-refresh)
2. Selects action (buy/sell/hold/limit_buy/limit_sell) and amount
3. For limit orders: Sets target price and places order without advancing turn
4. For market orders: Shows fee estimates and total cost/net proceeds
5. Clicks "Next Turn" to execute market trade (or advance time for limit orders)
6. New interval data fetched, chart slides forward one interval
7. Trade executes at new interval's price with fees deducted, balances update
8. Limit orders automatically execute if price conditions are met
9. Chart title updates to show current time window

### UI Layout
- **Compact Design**: 5-column control layout with inline status
- **Split View**: Chart (3.5 width) | Trading Panel (1.5 width)
- **Trading Panel**: Portfolio metrics, action controls, limit order management, fee estimates, persistent history
- **Smart Inputs**: Remember user preferences, validate against available funds including fees, price validation for limit orders
- **Fee Display**: Real-time fee estimates showing trading fees, gas fees, and total costs
- **Order Management**: Active limit orders display with cancel functionality and automatic execution notifications

### Session State Management
Critical state variables:
- `trading_mode`: Boolean for mode switching
- `cash_balance`, `btc_balance`: Portfolio values
- `current_price`: Latest BTC price for calculations
- `turn_number`: Current turn counter
- `trading_history`: Persistent list of all actions
- `limit_orders`: List of active limit orders with execution logic
- `last_buy_amount`, `last_sell_amount`: User preference memory
- `current_data_end_time`: Sliding window position for turn progression
- `cached_chart_data`: Preserves chart when toggling trading mode

## Dependencies
Core libraries: streamlit, yfinance, plotly, pandas, pytz, random, numpy
See requirements.txt for complete list.

## Recent Changes
- **Limit Order System**: Added comprehensive limit order functionality with automatic execution
- **Enhanced Fee Structure**: 0.5% taker fee (market orders) + 0.25% maker fee (limit orders) + dynamic gas fees ($15-50)
- **Order Management**: Active limit orders display, cancellation, and execution tracking
- **UI Enhancements**: Limit price inputs, price validation warnings, enhanced action buttons
- **Execution Engine**: `check_and_execute_limit_orders()` function runs each turn to process pending orders
- **Trading History**: Extended to include limit order placement, execution, cancellation, and detailed fee breakdowns
- **Session State**: Added `limit_orders` list to maintain active orders across turns
