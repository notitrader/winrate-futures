import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io

def simulate_trades(contracts, min_ticks_profit, max_ticks_profit, ticks_loss, tick_value, fee_per_contract, num_trades, zero_trade_rate, adjusted_win_rate, num_variations):
    simulation_results = {}
    ticks_used = {}

    for variation in range(1, num_variations + 1):
        profits = []
        ticks = []
        for _ in range(num_trades):
            random_value = np.random.rand()
            if random_value <= zero_trade_rate:
                profit = -(fee_per_contract * contracts * 2)  # Only fees paid on opening and closing
                ticks.append(0)
            elif random_value <= zero_trade_rate + adjusted_win_rate:
                random_ticks_profit = np.random.randint(min_ticks_profit, max_ticks_profit + 1)
                profit = (random_ticks_profit * tick_value * contracts) - (fee_per_contract * contracts * 2)  # Winning trade minus fees
                ticks.append(random_ticks_profit)
            else:
                profit = -(ticks_loss * tick_value * contracts) - (fee_per_contract * contracts * 2)  # Losing trade plus fees
                ticks.append(-ticks_loss)
            profits.append(profit)
        cumulative_profit = np.cumsum(profits)
        simulation_results[f'Variation {variation}'] = cumulative_profit
        ticks_used[f'Ticks {variation}'] = ticks

    return simulation_results, ticks_used

def calculate_metrics(df_simulation, selected_variations):
    average_cumulative_profit = df_simulation[selected_variations].iloc[-1].mean()
    drawdown = df_simulation[selected_variations].cummax() - df_simulation[selected_variations]
    max_drawdown = drawdown.max().max()

    returns = df_simulation[selected_variations].pct_change().mean()
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)

    return average_cumulative_profit, max_drawdown, sharpe_ratio

# Page configuration
st.title("Contract-Based Trading Simulator")

# User input
contracts = st.sidebar.selectbox("Number of Contracts", [1, 2, 3, 4])
min_ticks_profit = st.sidebar.number_input("Minimum Profit Ticks", min_value=1, max_value=10, value=3)
max_ticks_profit = st.sidebar.number_input("Maximum Profit Ticks", min_value=1, max_value=10, value=7)
ticks_loss = st.sidebar.number_input("Loss Ticks", min_value=1, max_value=10, value=5)
tick_value = st.sidebar.number_input("Tick Value ($)", min_value=0.01, value=12.5, step=0.01)
fee_per_contract = st.sidebar.number_input("Fee per Contract ($)", min_value=0.01, value=2.5, step=0.01)
num_trades = st.sidebar.number_input("Number of Trades", min_value=1, max_value=1000, value=200)
zero_trade_rate = st.sidebar.slider("Zero-Close Percentage (%)", min_value=0, max_value=100, value=10) / 100
win_rate = st.sidebar.slider("Win Percentage (%)", min_value=0, max_value=100, value=60) / 100

# Calculating effective percentages
adjusted_win_rate = win_rate * (1 - zero_trade_rate)
loss_rate = 1 - adjusted_win_rate - zero_trade_rate

# Modify the maximum number of variations to 50
num_variations = st.sidebar.number_input("Number of Variations", min_value=1, max_value=50, value=10)

# Simulation
simulation_results, ticks_used = simulate_trades(contracts, min_ticks_profit, max_ticks_profit, ticks_loss, tick_value, fee_per_contract, num_trades, zero_trade_rate, adjusted_win_rate, num_variations)

# Creating DataFrame to display results
df_simulation = pd.DataFrame(simulation_results)
df_ticks = pd.DataFrame(ticks_used)

# Combining the two DataFrames to have alternating columns of profits and ticks
df_combined
