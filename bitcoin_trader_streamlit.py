import streamlit as st
import datetime as dt
import pytz
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import random
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bitcoin_trader_streamlit.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

def calculate_trading_fees(trade_amount, trade_type='taker'):
    """
    Calculate realistic trading fees for Bitcoin transactions.
    
    Args:
        trade_amount: USD amount of the trade
        trade_type: 'maker' (0.25%) or 'taker' (0.5%) fee
    
    Returns:
        tuple: (trading_fee, gas_fee, total_fees)
    """
    # Trading fees (typical for crypto exchanges)
    if trade_type == 'maker':
        trading_fee_rate = 0.0025  # 0.25%
    else:  # taker
        trading_fee_rate = 0.005   # 0.5%
    
    trading_fee = trade_amount * trading_fee_rate
    
    # Simulate network gas fees ($15-50 range)
    # Higher fees for larger transactions to simulate network congestion
    base_gas = 15.0
    if trade_amount > 5000:
        gas_multiplier = 1 + (trade_amount - 5000) / 20000  # Increases with trade size
        gas_multiplier = min(gas_multiplier, 3.33)  # Cap at $50
    else:
        gas_multiplier = 1.0
    
    # Add some randomness to simulate network conditions
    random_factor = np.random.uniform(0.8, 1.2)
    gas_fee = base_gas * gas_multiplier * random_factor
    gas_fee = min(gas_fee, 50.0)  # Cap at $50
    
    total_fees = trading_fee + gas_fee
    
    return trading_fee, gas_fee, total_fees

def main():
    st.set_page_config(
        page_title="Bitcoin Historical Data Viewer",
        page_icon="₿",
        layout="wide"
    )
    
    # Compact header
    st.markdown("## ₿ Bitcoin Historical Data Viewer")
    st.markdown("---")
    
    # Detect user's local timezone with better logic
    def detect_local_timezone():
        try:
            # Try multiple methods to detect timezone
            import time
            # Method 1: Use time.tzname
            if hasattr(time, 'tzname') and time.tzname[0]:
                tz_name = time.tzname[1] if time.daylight and time.tzname[1] else time.tzname[0]
                # Handle common timezone abbreviations
                tz_mapping = {
                    'PST': 'US/Pacific', 'PDT': 'US/Pacific',
                    'MST': 'US/Mountain', 'MDT': 'US/Mountain', 
                    'CST': 'US/Central', 'CDT': 'US/Central',
                    'EST': 'US/Eastern', 'EDT': 'US/Eastern',
                }
                tz_name = tz_mapping.get(tz_name, tz_name)
                if tz_name in pytz.all_timezones:
                    return pytz.timezone(tz_name)
            
            # Method 2: Try to get from system
            try:
                import datetime
                local_tz_name = str(datetime.datetime.now().astimezone().tzinfo)
                if local_tz_name in pytz.all_timezones:
                    return pytz.timezone(local_tz_name)
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Timezone detection method failed: {e}")
        
        return pytz.timezone('UTC')
    
    detected_tz = detect_local_timezone()
    logger.debug(f"Detected timezone: {detected_tz}")
    
    # Initialize trading state in session state
    if 'trading_initialized' not in st.session_state:
        st.session_state.trading_initialized = True
        st.session_state.cash_balance = 10000.0  # Starting cash in USD
        st.session_state.btc_balance = 0.0       # Starting BTC balance
        st.session_state.trading_mode = False    # Whether trading mode is enabled
        st.session_state.turn_number = 0         # Current turn number
        st.session_state.trading_history = []    # List of trading transactions
        st.session_state.current_price = 0.0     # Current BTC price for calculations
        st.session_state.last_buy_amount = 1000.0  # Remember last buy amount
        st.session_state.last_sell_amount = 100.0  # Remember last sell amount
        logger.info("Trading state initialized")
    
    # Handle turn progression ONLY if next turn was explicitly triggered
    turn_was_triggered = False
    if 'next_turn_triggered' in st.session_state and st.session_state.next_turn_triggered:
        action = st.session_state.get('next_turn_action', 'hold')
        amount = st.session_state.get('next_turn_amount', 0.0)
        
        # Store for trading execution and clear the trigger
        st.session_state.last_turn_action = action
        st.session_state.last_turn_amount = amount
        
        # Clear the trigger flags
        st.session_state.next_turn_triggered = False
        if 'next_turn_action' in st.session_state:
            del st.session_state.next_turn_action
        if 'next_turn_amount' in st.session_state:
            del st.session_state.next_turn_amount
        
        # Increment turn number
        st.session_state.turn_number += 1
        turn_was_triggered = True
        
        # Store current data for next interval fetching
        if 'current_data_end_time' not in st.session_state:
            # First turn - store the end time of current data
            st.session_state.current_data_end_time = None
            st.session_state.turn_progression_mode = True
        
        logger.info(f"Processing turn {st.session_state.turn_number} with action: {action}")
        
        if action != "hold":
            logger.info(f"Trade action: {action} ${amount:.2f}")
    
    # Get current system time minus one hour for default
    now = dt.datetime.now()
    one_hour_ago = now - dt.timedelta(hours=1)
    
    # Initialize default values
    default_date = st.session_state.get('selected_date', one_hour_ago.date())
    default_hour = st.session_state.get('selected_hour', one_hour_ago.hour)
    
    # Find closest 15-minute interval for default
    minute_options = [0, 15, 30, 45]
    default_minute = st.session_state.get('selected_minute', min(minute_options, key=lambda x: abs(x - one_hour_ago.minute)))
    default_minute_index = minute_options.index(default_minute)
    
    # Common timezone options
    timezone_options = {
        str(detected_tz): f"Auto-detected ({detected_tz})",
        "US/Eastern": "US Eastern",
        "US/Central": "US Central", 
        "US/Mountain": "US Mountain",
        "US/Pacific": "US Pacific",
        "Europe/London": "London",
        "Europe/Paris": "Paris/Berlin",
        "Asia/Tokyo": "Tokyo",
        "Asia/Shanghai": "Shanghai",
        "Australia/Sydney": "Sydney",
        "UTC": "UTC"
    }
    
    # Compact controls layout
    col1, col2, col3, col4, col5 = st.columns([2.5, 1.5, 1.5, 2, 2.5])
    
    with col1:
        selected_date = st.date_input(
            "Date",
            value=default_date,
            help="Choose the date for Bitcoin data",
            key="date_input"
        )
    
    with col2:
        selected_hour = st.selectbox(
            "Hour",
            options=list(range(24)),
            index=default_hour,
            format_func=lambda x: f"{x:02d}",
            key="hour_input"
        )
    
    with col3:
        selected_minute = st.selectbox(
            "Min",
            options=minute_options,
            index=default_minute_index,
            format_func=lambda x: f"{x:02d}",
            key="minute_input"
        )
    
    with col4:
        # Interval selector
        interval_options = {
            "5m": "5 min",
            "10m": "10 min",
            "15m": "15 min",
            "30m": "30 min",
            "1h": "1 hour"
        }
        
        selected_interval = st.selectbox(
            "Interval",
            options=list(interval_options.keys()),
            format_func=lambda x: interval_options[x],
            index=0,  # Default to 5 minutes
            help="Choose the time interval for data points",
            key="interval_input"
        )
    
    with col5:
        # Timezone selector
        selected_timezone_str = st.selectbox(
            "Timezone",
            options=list(timezone_options.keys()),
            format_func=lambda x: timezone_options[x],
            index=0,  # Default to auto-detected
            help="Choose your timezone",
            key="timezone_input"
        )
        local_tz = pytz.timezone(selected_timezone_str)
    
    # Update session state with current selections
    st.session_state.selected_date = selected_date
    st.session_state.selected_hour = selected_hour
    st.session_state.selected_minute = selected_minute
    
    # Check if inputs have changed to trigger auto-refresh (only when not in trading mode)
    turn_progression = st.session_state.get('turn_progression_mode', False)
    trading_mode = st.session_state.get('trading_mode', False)
    
    if not turn_progression and not trading_mode:
        current_inputs = f"{selected_date}_{selected_hour}_{selected_minute}_{selected_interval}_{selected_timezone_str}"
        previous_inputs = st.session_state.get('previous_inputs', '')
        
        auto_fetch = current_inputs != previous_inputs
        st.session_state.previous_inputs = current_inputs
    else:
        auto_fetch = False
    
    # Compact action row
    btn_col1, btn_col2 = st.columns([2, 8])
    
    with btn_col1:
        # Random date button
        if st.button("🎲 Random", help="Pick random date/time in past 45 days"):
            # Calculate 45 days ago from now
            forty_five_days_ago = now - dt.timedelta(days=45)
            
            # Generate random date between 45 days ago and now
            time_between = now - forty_five_days_ago
            random_days = random.randint(0, time_between.days)
            random_date = forty_five_days_ago + dt.timedelta(days=random_days)
            
            # Generate random hour and minute (15-minute intervals)
            random_hour = random.randint(0, 23)
            random_minute = random.choice([0, 15, 30, 45])
            
            # Store in session state
            st.session_state.selected_date = random_date.date()
            st.session_state.selected_hour = random_hour
            st.session_state.selected_minute = random_minute
            st.rerun()
    
    with btn_col2:
        # Status info
        if auto_fetch:
            st.info("🔄 Auto-refreshing...")
        elif trading_mode:
            st.info("🎮 Trading mode: Use 'Next Turn' to progress")
        else:
            st.info(f"📍 {timezone_options[selected_timezone_str]}")
    
    # No manual fetch button needed since auto-refresh handles everything
    manual_fetch = False
    
    # Force fetch on turn progression ONLY when explicitly triggered
    turn_fetch = turn_was_triggered and turn_progression
    
    # Create main layout: chart on left, trading panel on right
    chart_col, trading_col = st.columns([3.5, 1.5])

    # Show chart column content when no data fetch is happening
    with chart_col:
        if not (auto_fetch or manual_fetch or turn_fetch):
            # Check if we have cached chart data to display
            if 'cached_chart_data' in st.session_state and st.session_state.cached_chart_data is not None:
                # Display cached chart
                cached_data, cached_fig = st.session_state.cached_chart_data
                
                # Update current price for trading
                st.session_state.current_price = cached_data['Close'].iloc[-1]
                
                # Display the cached chart
                st.plotly_chart(cached_fig, use_container_width=True)
                
                # Compact summary statistics
                s_col1, s_col2, s_col3, s_col4 = st.columns(4)
                with s_col1:
                    st.metric("Open", f"${cached_data['Open'].iloc[0]:,.0f}")
                with s_col2:
                    st.metric("Close", f"${cached_data['Close'].iloc[-1]:,.0f}")
                with s_col3:
                    st.metric("High", f"${cached_data['High'].max():,.0f}")
                with s_col4:
                    st.metric("Low", f"${cached_data['Low'].min():,.0f}")
                
                # Compact data table
                with st.expander("📋 Raw Data", expanded=False):
                    st.dataframe(cached_data, use_container_width=True, height=200)
            else:
                st.info("Select date/time settings and click 'Fetch Bitcoin Data' to view the chart")

    if auto_fetch or manual_fetch or turn_fetch:
        if auto_fetch:
            logger.info("Auto-refreshing data due to input change")
        elif turn_fetch:
            logger.info("Turn progression data fetch")
        else:
            logger.info("Manual data fetch triggered")
        logger.info("Starting data fetch process")
        
        try:
            # Create datetime object in local timezone
            local_dt = dt.datetime.combine(selected_date, dt.time(selected_hour, selected_minute))
            local_dt = local_tz.localize(local_dt)
            logger.debug(f"Local datetime: {local_dt}")
            
            # Convert to UTC for API call
            utc_dt = local_dt.astimezone(pytz.UTC)
            logger.debug(f"UTC datetime: {utc_dt}")
            
            # Calculate time range based on interval and trading mode
            if turn_progression and 'current_data_end_time' in st.session_state and st.session_state.current_data_end_time:
                # In turn progression mode, fetch next interval from where we left off
                interval_minutes = {
                    '5m': 5, '10m': 10, '15m': 15, '30m': 30, '1h': 60
                }[selected_interval]
                
                # Start from the last end time
                start_dt = st.session_state.current_data_end_time
                # Fetch enough data to get one more interval plus some buffer
                end_dt = start_dt + dt.timedelta(minutes=interval_minutes * 2)
                hours_back = 6  # Get extra data for sliding window
                extended_start = start_dt - dt.timedelta(hours=hours_back)
                
                logger.info(f"Turn progression: fetching from {start_dt} to {end_dt}")
            else:
                # Normal mode or first turn
                if selected_interval in ['5m', '10m', '15m', '30m']:
                    # For minute intervals, get 5 hours of data
                    hours_back = 5
                    # Calculate end time to ensure we get enough data
                    end_dt = utc_dt + dt.timedelta(hours=1)
                else:  # 1h interval
                    # For hourly interval, get 5 hours of data
                    hours_back = 5
                    end_dt = utc_dt + dt.timedelta(hours=1)
                
                start_dt = utc_dt - dt.timedelta(hours=hours_back)
                extended_start = start_dt
            logger.debug(f"Start datetime: {start_dt}")
            logger.debug(f"End datetime: {end_dt}")
            logger.debug(f"Selected interval: {selected_interval}")
            
            # Check if the selected time is in the future
            if utc_dt > dt.datetime.now(pytz.UTC):
                st.error("⚠️ Cannot fetch data for future dates/times!")
                logger.warning("User selected future date/time")
                return
            
            # Show loading spinner
            with st.spinner("Fetching Bitcoin data from Yahoo Finance..."):
                # Fetch Bitcoin data
                logger.info("Fetching Bitcoin data from Yahoo Finance")
                btc = yf.Ticker("BTC-USD")
                
                # Get data with selected interval
                fetch_start = extended_start if turn_progression and 'current_data_end_time' in st.session_state and st.session_state.current_data_end_time else start_dt
                data = btc.history(
                    start=fetch_start,
                    end=end_dt,
                    interval=selected_interval
                )
                
                logger.info(f"Fetched {len(data)} data points")
                logger.debug(f"Data shape: {data.shape}")
                logger.debug(f"Data columns: {data.columns.tolist()}")
            
            if data.empty:
                st.error("❌ No data available for the selected time period!")
                logger.error("No data returned from Yahoo Finance")
                return
            
            # Filter data to show exactly 5 hours ending at the selected time
            # Convert data index to UTC for comparison
            data_utc = data.copy()
            data_utc.index = data_utc.index.tz_convert(pytz.UTC) if data_utc.index.tz is not None else data_utc.index.tz_localize(pytz.UTC)
            
            # Calculate how many data points to show based on interval
            if selected_interval == '5m':
                data_points = 60   # 5 hours * 12 intervals per hour
            elif selected_interval == '10m':
                data_points = 30   # 5 hours * 6 intervals per hour
            elif selected_interval == '15m':
                data_points = 20   # 5 hours * 4 intervals per hour
            elif selected_interval == '30m':
                data_points = 10   # 5 hours * 2 intervals per hour
            else:  # 1h
                data_points = 5    # 5 hours * 1 interval per hour
            
            if turn_progression:
                # Execute trading action from session state
                action = st.session_state.get('last_turn_action')
                amount = st.session_state.get('last_turn_amount', 0.0)
                
                if st.session_state.current_data_end_time is None:
                    # First turn - use the latest data point for trading
                    filtered_data = data_utc[data_utc.index <= utc_dt].tail(data_points)
                    new_price = filtered_data['Close'].iloc[-1]  # Use close price of last interval
                    st.session_state.current_data_end_time = filtered_data.index.max()
                else:
                    # Subsequent turns - get new data point
                    new_data_point = data_utc[data_utc.index > st.session_state.current_data_end_time]
                    if not new_data_point.empty:
                        newest_point = new_data_point.iloc[0]
                        new_price = newest_point['Open']  # Use open price for trading
                        # Update the end time for next turn
                        st.session_state.current_data_end_time = data_utc.index.max()
                        # Get sliding window of data
                        filtered_data = data_utc.tail(data_points)
                    else:
                        # No new data available, use existing
                        filtered_data = data_utc.tail(data_points)
                        new_price = filtered_data['Close'].iloc[-1]
                
                # Execute trading action
                if action and action != "hold":
                    if action == "buy" and amount > 0:
                        # Calculate fees first
                        trading_fee, gas_fee, total_fees = calculate_trading_fees(amount, 'taker')
                        total_cost = amount + total_fees
                        
                        if total_cost <= st.session_state.cash_balance:
                            btc_bought = amount / new_price  # BTC bought with gross amount
                            st.session_state.cash_balance -= total_cost  # Deduct gross + fees
                            st.session_state.btc_balance += btc_bought
                            
                            # Record transaction
                            st.session_state.trading_history.append({
                                'turn': st.session_state.turn_number,
                                'action': 'buy',
                                'amount': amount,
                                'price': new_price,
                                'btc_amount': btc_bought,
                                'trading_fee': trading_fee,
                                'gas_fee': gas_fee,
                                'total_fees': total_fees,
                                'total_cost': total_cost
                            })
                        else:
                            # Record failed transaction attempt
                            st.session_state.trading_history.append({
                                'turn': st.session_state.turn_number,
                                'action': 'buy_failed',
                                'amount': amount,
                                'price': new_price,
                                'error': f'Insufficient cash balance (need ${total_cost:.2f} including fees)'
                            })
                    
                    elif action == "sell" and amount > 0:
                        btc_to_sell = amount / new_price
                        if btc_to_sell <= st.session_state.btc_balance:
                            # Calculate fees on the sell amount
                            trading_fee, gas_fee, total_fees = calculate_trading_fees(amount, 'taker')
                            net_proceeds = amount - total_fees
                            
                            st.session_state.btc_balance -= btc_to_sell
                            st.session_state.cash_balance += net_proceeds  # Add net proceeds after fees
                            
                            # Record transaction
                            st.session_state.trading_history.append({
                                'turn': st.session_state.turn_number,
                                'action': 'sell',
                                'amount': amount,
                                'price': new_price,
                                'btc_amount': btc_to_sell,
                                'trading_fee': trading_fee,
                                'gas_fee': gas_fee,
                                'total_fees': total_fees,
                                'net_proceeds': net_proceeds
                            })
                        else:
                            # Record failed transaction attempt
                            st.session_state.trading_history.append({
                                'turn': st.session_state.turn_number,
                                'action': 'sell_failed',
                                'amount': amount,
                                'price': new_price,
                                'error': 'Insufficient BTC balance'
                            })
                
                elif action == "hold":
                    # Record hold action
                    st.session_state.trading_history.append({
                        'turn': st.session_state.turn_number,
                        'action': 'hold',
                        'amount': 0,
                        'price': new_price
                    })
                
                # Update current price after trading
                st.session_state.current_price = new_price
                
            else:
                # Normal mode
                filtered_data = data_utc[data_utc.index <= utc_dt].tail(data_points)
            
            if filtered_data.empty:
                st.error("❌ No data available for the selected time period!")
                logger.error("No data available after filtering")
                return
            
            # Use filtered data
            data = filtered_data
            
            # Display data info
            interval_name = interval_options[selected_interval]
            st.success(f"✅ Successfully fetched {len(data)} data points ({interval_name} intervals) of Bitcoin data")
            
            # Create candlestick chart using Plotly
            logger.info("Creating candlestick chart")
            
            fig = go.Figure(data=go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="BTC-USD"
            ))
            
            # Generate chart title based on current data endpoint
            if turn_progression and 'current_data_end_time' in st.session_state and st.session_state.current_data_end_time:
                # In turn progression mode, use the latest data point time
                latest_time = data.index.max()
                if latest_time.tz is not None:
                    latest_local = latest_time.tz_convert(local_tz)
                else:
                    latest_local = latest_time.tz_localize(pytz.UTC).tz_convert(local_tz)
                chart_title = f'BTC-USD: 5h Before {latest_local.strftime("%Y-%m-%d %H:%M")} ({interval_name})'
            else:
                # Normal mode, use original selected time
                chart_title = f'BTC-USD: 5h Before {local_dt.strftime("%Y-%m-%d %H:%M")} ({interval_name})'
            
            fig.update_layout(
                title=chart_title,
                xaxis_title='Time (UTC)',
                yaxis_title='Price (USD)',
                height=450,
                xaxis_rangeslider_visible=False,
                template="plotly_white",
                margin=dict(t=50, b=40, l=40, r=40)
            )
            
            # Cache the chart data and figure for when trading mode is toggled
            st.session_state.cached_chart_data = (data.copy(), fig)
            
            with chart_col:
                # Update current price for trading calculations
                st.session_state.current_price = data['Close'].iloc[-1]
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Compact summary statistics
                s_col1, s_col2, s_col3, s_col4 = st.columns(4)
                with s_col1:
                    st.metric("Open", f"${data['Open'].iloc[0]:,.0f}")
                with s_col2:
                    st.metric("Close", f"${data['Close'].iloc[-1]:,.0f}")
                with s_col3:
                    st.metric("High", f"${data['High'].max():,.0f}")
                with s_col4:
                    st.metric("Low", f"${data['Low'].min():,.0f}")
                
                # Compact data table
                with st.expander("📋 Raw Data", expanded=False):
                    st.dataframe(data, use_container_width=True, height=200)
            
            logger.info("Chart display completed successfully")
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error in fetch_and_display_data: {str(e)}", exc_info=True)
    
    # Trading panel (always displayed, will have updated prices after data fetch)
    with trading_col:
        # Compact trading panel
        st.markdown("#### 💰 Trading")
        
        # Toggle trading mode
        trading_enabled = st.checkbox("Enable Trading", value=st.session_state.trading_mode)
        st.session_state.trading_mode = trading_enabled
        
        if trading_enabled:
            # Calculate portfolio values using current price (now updated after any trading)
            current_btc_usd_value = st.session_state.btc_balance * max(st.session_state.current_price, 1.0)
            total_portfolio = st.session_state.cash_balance + current_btc_usd_value
            
            # Use columns for compact metrics
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.metric("Cash", f"${st.session_state.cash_balance:,.0f}")
                st.metric("BTC", f"{st.session_state.btc_balance:.4f}")
            with p_col2:
                st.metric("BTC $", f"${current_btc_usd_value:,.0f}")
                st.metric("Total", f"${total_portfolio:,.0f}")
            
            st.metric("Price", f"${st.session_state.current_price:,.2f}")
            
            # Compact trading controls
            action = st.selectbox(
                "Action",
                options=["hold", "buy", "sell"],
                format_func=lambda x: x.title(),
                key=f"trading_action_turn_{st.session_state.turn_number}"
            )
            
            # Trade amount input
            if action != "hold":
                if action == "buy":
                    # Calculate max buy considering fees
                    # Estimate fees for max amount (approximate)
                    temp_trading_fee = st.session_state.cash_balance * 0.005
                    temp_gas_fee = min(15.0 + (st.session_state.cash_balance / 20000) * 15.0, 50.0)
                    estimated_fees = temp_trading_fee + temp_gas_fee
                    max_amount = max(0, st.session_state.cash_balance - estimated_fees)
                    st.caption(f"Max: ~${max_amount:,.0f} (after fees)")
                    # Use last buy amount, but cap it at available cash minus fees
                    default_amount = min(st.session_state.last_buy_amount, max_amount)
                else:  # sell
                    max_amount = current_btc_usd_value
                    st.caption(f"Max: ${max_amount:,.0f} (fees deducted from proceeds)")
                    # Use last sell amount, but cap it at available BTC value
                    default_amount = min(st.session_state.last_sell_amount, max_amount)
                
                if max_amount > 0:
                    trade_amount = st.number_input(
                        "Amount ($)",
                        min_value=0.01,
                        max_value=max_amount,
                        value=default_amount,
                        step=0.01,
                        key=f"trade_amount_turn_{st.session_state.turn_number}"
                    )
                    
                    # Show fee estimate
                    if trade_amount > 0:
                        est_trading_fee, est_gas_fee, est_total_fees = calculate_trading_fees(trade_amount, 'taker')
                        if action == "buy":
                            st.caption(f"Est. fees: ${est_total_fees:.2f} (trading: ${est_trading_fee:.2f}, gas: ${est_gas_fee:.2f})")
                            st.caption(f"Total cost: ${trade_amount + est_total_fees:.2f}")
                        else:  # sell
                            st.caption(f"Est. fees: ${est_total_fees:.2f} (trading: ${est_trading_fee:.2f}, gas: ${est_gas_fee:.2f})")
                            st.caption(f"Net proceeds: ${trade_amount - est_total_fees:.2f}")
                    
                    # Update last amount when user changes it
                    if action == "buy":
                        st.session_state.last_buy_amount = trade_amount
                    else:  # sell
                        st.session_state.last_sell_amount = trade_amount
                else:
                    st.warning("No funds")
                    trade_amount = 0
            
            # Compact action buttons
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("▶️ Next", type="primary", key="next_turn_btn", use_container_width=True):
                    # Set the trigger flag and store the action
                    st.session_state.next_turn_triggered = True
                    st.session_state.next_turn_action = action
                    if action != "hold":
                        if action == "buy":
                            max_for_action = st.session_state.cash_balance
                        else:  # sell
                            max_for_action = current_btc_usd_value
                        
                        if max_for_action > 0:
                            st.session_state.next_turn_amount = trade_amount
                        else:
                            st.session_state.next_turn_amount = 0.0
                    logger.info(f"Next Turn button clicked - Action: {action}")
                    st.rerun()
            
            with btn2:
                if st.button("🔄 Reset", help="Reset trading", use_container_width=True):
                    # Reset all trading state
                    st.session_state.cash_balance = 10000.0
                    st.session_state.btc_balance = 0.0
                    st.session_state.turn_number = 0
                    st.session_state.trading_history = []
                    st.session_state.turn_progression_mode = False
                    st.session_state.last_buy_amount = 1000.0
                    st.session_state.last_sell_amount = 100.0
                    if 'current_data_end_time' in st.session_state:
                        del st.session_state.current_data_end_time
                    st.success("Reset!")
                    st.rerun()
            
            # Turn info and history
            st.caption(f"Turn: {st.session_state.turn_number}")
            
            if st.session_state.trading_history:
                with st.expander("Trading History", expanded=True):
                    # Show last 10 trades, most recent first
                    for trade in reversed(st.session_state.trading_history[-10:]):
                        if trade['action'] == 'buy':
                            if 'total_fees' in trade:
                                st.success(f"T{trade['turn']}: Bought {trade['btc_amount']:.4f} BTC for ${trade['amount']:.0f} @ ${trade['price']:.0f} (fees: ${trade['total_fees']:.2f})")
                            else:
                                st.success(f"T{trade['turn']}: Bought {trade['btc_amount']:.4f} BTC for ${trade['amount']:.0f} @ ${trade['price']:.0f}")
                        elif trade['action'] == 'sell':
                            if 'total_fees' in trade:
                                st.error(f"T{trade['turn']}: Sold {trade['btc_amount']:.4f} BTC for ${trade['amount']:.0f} @ ${trade['price']:.0f} (fees: ${trade['total_fees']:.2f})")
                            else:
                                st.error(f"T{trade['turn']}: Sold {trade['btc_amount']:.4f} BTC for ${trade['amount']:.0f} @ ${trade['price']:.0f}")
                        elif trade['action'] == 'hold':
                            st.info(f"T{trade['turn']}: Held position @ ${trade['price']:.0f}")
                        elif trade['action'] == 'buy_failed':
                            st.warning(f"T{trade['turn']}: Buy failed - {trade['error']}")
                        elif trade['action'] == 'sell_failed':
                            st.warning(f"T{trade['turn']}: Sell failed - {trade['error']}")
        
        else:
            st.info("Enable trading to start with $10,000")

if __name__ == "__main__":
    main()