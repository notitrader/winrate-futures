import streamlit as st
import numpy as np
import pandas as pd

# Configurazione della pagina
st.title("Simulatore di Trading basato sui Contratti")

# Input dell'utente
contracts = st.sidebar.selectbox("Numero di Contratti", [1, 2, 3, 4])
ticks_profit = st.sidebar.number_input("Ticks di Profitto", min_value=1, max_value=10, value=5)
ticks_loss = st.sidebar.number_input("Ticks di Perdita", min_value=1, max_value=10, value=5)
tick_value = st.sidebar.number_input("Valore del Tick ($)", min_value=0.01, value=12.5, step=0.01)
fee_per_contract = st.sidebar.number_input("Costo delle Fee per Contratto ($)", min_value=0.01, value=2.5, step=0.01)
num_trades = st.sidebar.number_input("Numero di Operazioni", min_value=1, max_value=1000, value=200)
zero_trade_rate = st.sidebar.slider("Percentuale di Chiusura a 0 (%)", min_value=0, max_value=100, value=10) / 100
win_rate = st.sidebar.slider("Percentuale di Vincita (%)", min_value=0, max_value=100, value=60) / 100

# Calcolo delle percentuali effettive
adjusted_win_rate = win_rate * (1 - zero_trade_rate)
loss_rate = 1 - adjusted_win_rate - zero_trade_rate

num_variations = st.sidebar.number_input("Numero di Variazioni", min_value=1, max_value=20, value=10)

# Simulazione
simulation_results = {}

for variation in range(1, num_variations + 1):
    profits = []
    for _ in range(num_trades):
        random_value = np.random.rand()
        if random_value <= zero_trade_rate:
            profit = -(fee_per_contract * contracts * 2)  # Solo fee pagate in apertura e chiusura
        elif random_value <= zero_trade_rate + adjusted_win_rate:
            profit = (ticks_profit * tick_value * contracts) - (fee_per_contract * contracts * 2)  # Trade vincente meno fee
        else:
            profit = -(ticks_loss * tick_value * contracts) - (fee_per_contract * contracts * 2)  # Trade perdente più fee
        profits.append(profit)
    cumulative_profit = np.cumsum(profits)
    simulation_results[f'Variation {variation}'] = cumulative_profit

# Creazione del DataFrame per visualizzare i risultati
df_simulation = pd.DataFrame(simulation_results)

# Calcolo della media dei profitti cumulativi
average_cumulative_profit = df_simulation.iloc[-1].mean()

# Visualizzazione dei risultati
st.subheader("Risultati della Simulazione")
st.line_chart(df_simulation)

# Visualizzazione della tabella dei profitti cumulativi
st.subheader("Tabella dei Profitti Cumulativi")
st.dataframe(df_simulation)

# Visualizzazione della media dei profitti cumulativi
st.subheader(f"Media dei Profitti Cumulativi: ${average_cumulative_profit:.2f}")
