import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import streamlit.components.v1 as components

# Page configuration
st.title("Contract-Based Trading Simulator")
st.markdown("""
Hi I'm Noti Trader and this is my trading simulator
""")
# Add the clickable image to the sidebar
st.sidebar.markdown(
    """
    <a href="https://notitrader.com/" target="_blank">
        <img src="https://notitrader.com/wp-content/uploads/2024/09/logo-noti-png.png" alt="Noti Trader Logo" style="width: 150px; margin-bottom: 20px;">
    </a>
    """,
    unsafe_allow_html=True
)
# Simulation Calculations
contracts = st.sidebar.selectbox("Number of Contracts", [1, 2, 3, 4])
min_ticks_profit = st.sidebar.number_input("Minimum Profit Ticks", min_value=1, max_value=300, value=3)
max_ticks_profit = st.sidebar.number_input("Maximum Profit Ticks", min_value=1, max_value=300, value=7)
ticks_loss = st.sidebar.number_input("Loss Ticks", min_value=1, max_value=200, value=5)
tick_value = st.sidebar.number_input("Tick Value ($)", min_value=0.01, value=12.5, step=0.01)
fee_per_contract = st.sidebar.number_input("Fee per Contract ($)", min_value=0.01, value=2.5, step=0.01)
num_trades = st.sidebar.number_input("Number of Trades", min_value=1, max_value=2000, value=200)
breakeven_trades = st.sidebar.slider("Breakeven Trades (%)", min_value=0, max_value=100, value=10) / 100
win_rate = st.sidebar.slider("Win Percentage (%)", min_value=0, max_value=100, value=60) / 100

# Ensure min_ticks_profit is less than max_ticks_profit
if min_ticks_profit >= max_ticks_profit:
    st.error("Minimum Profit Ticks must be less than Maximum Profit Ticks.")
else:
    # Calculating effective percentages
    adjusted_win_rate = win_rate * (1 - breakeven_trades)
    loss_rate = 1 - adjusted_win_rate - breakeven_trades

    # Modify the maximum number of variations
    num_variations = st.sidebar.number_input("Number of Variations", min_value=1, max_value=50, value=10)

    # Simulation
    simulation_results = {}
    ticks_used = {}

    for variation in range(1, num_variations + 1):
        profits = []
        ticks = []
        for _ in range(num_trades):
            random_value = np.random.rand()
            if random_value <= breakeven_trades:
                profit = -(fee_per_contract * contracts * 2)  # Only fees paid on opening and closing
                ticks.append(0)
            elif random_value <= breakeven_trades + adjusted_win_rate:
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

    # Replace NaN, inf, and -inf with 0 for display purposes
    df_simulation.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
    df_ticks.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

    # Convert ticks to string to prevent display issues
    df_ticks = df_ticks.applymap(str)

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
    options = ["All Variations"] + df_simulation.columns.tolist()
    selected_variation = st.sidebar.selectbox("Variation", options)

    # Calculating metrics
    if selected_variation == "All Variations":
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
    if selected_variation == "All Variations":
        st.dataframe(df_combined)
    else:
        st.dataframe(df_combined[[selected_variation]])

    # Download results as CSV
    st.subheader("Download Results")
    if selected_variation == "All Variations":
        csv = df_combined.to_csv(index=False)
    else:
        csv = df_combined[[selected_variation]].to_csv(index=False)
    b = io.BytesIO()
    b.write(csv.encode())
    b.seek(0)
    st.download_button(label="Download as CSV", data=b, file_name="simulation_results.csv", mime="text/csv")
    # Desc
st.markdown("""
**Ultimate Trading Simulator designed for contract-based trading and futures for trading enthusiasts.**  

This powerful tool allows traders to simulate and analyze their strategies, focusing on **Risk Management** and **Profit/Loss Simulation**.  
By configuring key parameters such as Stop Loss settings, Tick Value, and Win Rate, users can **Backtest Trading Strategies** and assess their **Trading Performance** in a realistic environment.

Our **Risk Management Simulator** enables you to simulate up to 1000 trades with customizable Futures Contracts and provides detailed insights through **Cumulative Profit Analysis**.  
Whether you're looking to improve your Win Rate or understand the impact of Trading Fees, this Trade Simulation Tool offers a comprehensive solution for traders at all levels.

With features like **Advanced Trading Analytics**, detailed **Profit/Loss Distribution** charts, and the ability to **Download Trading Simulations**, you can optimize your trading strategy with confidence.  
Perfect for both beginners and seasoned professionals, this app provides everything you need to take your trading performance to the next level.

Discover my Trading Journal created with Notion: [https://notitrader.com/](https://notitrader.com/)

""")


# Creare un componente HTML per Google Analytics
GA_TRACKING_ID = 'G-57S9M5V2N6'
ga_code = f"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_TRACKING_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{GA_TRACKING_ID}');
</script>
"""

# Iniettare il codice nel componente Streamlit
components.html(ga_code)



