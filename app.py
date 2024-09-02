import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io

# Page configuration
st.title("Contract-Based Trading Simulator")

# Simulation Calculations
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
    ticks_used[f'Variation {variation}'] = ticks

# Creating DataFrame to display results
df_simulation = pd.DataFrame(simulation_results)
df_ticks = pd.DataFrame(ticks_used)

# Replace NaN or inf with 0 for display purposes
df_simulation.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

# Combine profits and ticks into a single DataFrame with a MultiIndex
combined_data = {}
for variation in range(1, num_variations + 1):
    combined_data[(f'Variation {variation}', 'Profits')] = df_simulation[f'Variation {variation}'].apply(lambda x: f"${x:,.2f}")
    combined_data[(f'Variation {variation}', 'Ticks')] = df_ticks[f'Variation {variation}']

df_combined = pd.DataFrame(combined_data)

# Set MultiIndex for columns
df_combined.columns = pd.MultiIndex.from_tuples(df_combined.columns, names=["Variation", "Type"])

# Selecting one variation to display or all
st.sidebar.subheader("Select Variation to Display")
options = ["Tutte le variazioni"] + df_simulation.columns.tolist()
selected_variation = st.sidebar.selectbox("Variation", options)

# Calculating metrics
if selected_variation == "Tutte le variazioni":
    selected_variations = df_simulation.columns.tolist()
    avg_profit = df_simulation[selected_variations].iloc[-1].mean()
    drawdown = df_simulation[selected_variations].cummax() - df_simulation[selected_variations]
    max_drawdown = drawdown.max().max()
    sharpe_ratio = (df_simulation[selected_variations].mean().mean() / df_simulation[selected_variations].std().mean()) * np.sqrt(252)
else:
    selected_variations = [selected_variation]
    avg_profit = df_simulation[selected_variation].iloc[-1].mean()
    drawdown = df_simulation[selected_variation].cummax() - df_simulation[selected_variation]
    max_drawdown = drawdown.max().max()
    sharpe_ratio = (df_simulation[selected_variation].mean() / df_simulation[selected_variation].std()) * np.sqrt(252)

# Display the calculated values as paragraphs
st.markdown(f"<p>Average Cumulative Profits: ${avg_profit:.2f}</p>", unsafe_allow_html=True)
st.markdown(f"<p>Maximum Drawdown: ${max_drawdown:.2f}</p>", unsafe_allow_html=True)
st.markdown(f"<p>Sharpe Ratio: {sharpe_ratio:.2f}</p>", unsafe_allow_html=True)

# Displaying results
st.subheader("Simulation Results")
st.line_chart(df_simulation[selected_variations], use_container_width=True)

# Displaying the table of cumulative profits and used ticks
st.subheader("Table of Cumulative Profits and Used Ticks")
if selected_variation == "Tutte le variazioni":
    st.dataframe(df_combined)
else:
    st.dataframe(df_combined[[selected_variation]])

# Download results as CSV
st.subheader("Download Results")
if selected_variation == "Tutte le variazioni":
    csv = df_combined.to_csv(index=False)
else:
    csv = df_combined[[selected_variation]].to_csv(index=False)
b = io.BytesIO()
b.write(csv.encode())
b.seek(0)
st.download_button(label="Download as CSV", data=b, file_name="simulation_results.csv", mime="text/csv")
