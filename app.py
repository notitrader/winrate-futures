import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io

# Configurazione della pagina
st.title("Simulatore di Trading basato sui Contratti")

# Input dell'utente
contracts = st.sidebar.selectbox("Numero di Contratti", [1, 2, 3, 4])
min_ticks_profit = st.sidebar.number_input("Minimo Ticks di Profitto", min_value=1, max_value=10, value=3)
max_ticks_profit = st.sidebar.number_input("Massimo Ticks di Profitto", min_value=1, max_value=10, value=7)
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
ticks_used = {}

for variation in range(1, num_variations + 1):
    profits = []
    ticks = []
    for _ in range(num_trades):
        random_value = np.random.rand()
        if random_value <= zero_trade_rate:
            profit = -(fee_per_contract * contracts * 2)  # Solo fee pagate in apertura e chiusura
            ticks.append(0)
        elif random_value <= zero_trade_rate + adjusted_win_rate:
            random_ticks_profit = np.random.randint(min_ticks_profit, max_ticks_profit + 1)
            profit = (random_ticks_profit * tick_value * contracts) - (fee_per_contract * contracts * 2)  # Trade vincente meno fee
            ticks.append(random_ticks_profit)
        else:
            profit = -(ticks_loss * tick_value * contracts) - (fee_per_contract * contracts * 2)  # Trade perdente più fee
            ticks.append(-ticks_loss)
        profits.append(profit)
    cumulative_profit = np.cumsum(profits)
    simulation_results[f'Variation {variation}'] = cumulative_profit
    ticks_used[f'Ticks {variation}'] = ticks

# Creazione del DataFrame per visualizzare i risultati
df_simulation = pd.DataFrame(simulation_results)
df_ticks = pd.DataFrame(ticks_used)

# Unione dei due DataFrame per avere colonne alternate di profitti e tick
df_combined = pd.concat([df_simulation, df_ticks], axis=1).sort_index(axis=1, key=lambda x: [int(i.split()[-1]) for i in x])

# Calcolo della media dei profitti cumulativi
average_cumulative_profit = df_simulation.iloc[-1].mean()

# Calcolo del drawdown massimo
drawdown = df_simulation.cummax() - df_simulation
max_drawdown = drawdown.max().max()

# Calcolo del Sharpe ratio (approssimativo)
sharpe_ratio = (df_simulation.mean().mean() / df_simulation.std().mean()) * np.sqrt(252)

# Visualizzazione dei risultati
st.subheader("Risultati della Simulazione")
st.line_chart(df_simulation, use_container_width=True)

# Visualizzazione della tabella dei profitti cumulativi e dei tick
st.subheader("Tabella dei Profitti Cumulativi e Tick Utilizzati")
st.dataframe(df_combined)

# Visualizzazione della media dei profitti cumulativi
st.subheader(f"Media dei Profitti Cumulativi: ${average_cumulative_profit:.2f}")

# Visualizzazione del drawdown massimo
st.subheader(f"Drawdown Massimo: ${max_drawdown:.2f}")

# Visualizzazione del Sharpe Ratio
st.subheader(f"Sharpe Ratio: {sharpe_ratio:.2f}")

# Download dei risultati come CSV
st.subheader("Scarica i Risultati")
csv = df_combined.to_csv(index=False)
b = io.BytesIO()
b.write(csv.encode())
b.seek(0)
st.download_button(label="Scarica come CSV", data=b, file_name="simulation_results.csv", mime="text/csv")
