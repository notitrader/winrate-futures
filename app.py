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

# Debugging output
st.write("Simulation Results", simulation_results)
st.write("Ticks Used", ticks_used)

# Creating DataFrame to display results
df_simulation = pd.DataFrame(simulation_results)
df_ticks = pd.DataFrame(ticks_used)

st.write("DataFrame Simulation", df_simulation)
st.write("DataFrame Ticks", df_ticks)

# Check for empty DataFrames
if df_simulation.empty or df_ticks.empty:
    st.error("Error: One or both of the DataFrames are empty. Check the simulation results and ticks used.")
else:
    # Combining the two DataFrames to have alternating columns of profits and ticks
    df_combined = pd.concat([df_simulation, df_ticks], axis=1).sort_index(axis=1, key=lambda x: [int(i.split()[-1]) for i in x])

    # Selecting variations to display
    st.sidebar.subheader("Select Variations to Display")
    selected_variations = st.sidebar.multiselect("Variations", df_simulation.columns.tolist(), default=df_simulation.columns.tolist())

    # Displaying results
    st.subheader("Simulation Results")
    st.line_chart(df_simulation[selected_variations], use_container_width=True)

    # Displaying the table of cumulative profits and used ticks
    st.subheader("Table of Cumulative Profits and Used Ticks")
    st.dataframe(df_combined)

    # Calculating metrics
    average_cumulative_profit, max_drawdown, sharpe_ratio = calculate_metrics(df_simulation, selected_variations)

    # Displaying the average cumulative profit
    st.subheader(f"Average Cumulative Profits: ${average_cumulative_profit:.2f}")

    # Displaying the maximum drawdown
    st.subheader(f"Maximum Drawdown: ${max_drawdown:.2f}")

    # Displaying the Sharpe Ratio
    st.subheader(f"Sharpe Ratio: {sharpe_ratio:.2f}")

    # Download results as CSV
    st.subheader("Download Results")
    csv = df_combined.to_csv(index=False)
    b = io.BytesIO()
    b.write(csv.encode())
    b.seek(0)
    st.download_button(label="Download as CSV", data=b, file_name="simulation_results.csv", mime="text/csv")
