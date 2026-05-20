import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Simple Plot", page_icon="📉", layout="wide")
st.title("📉 Einfaches Liniendiagramm mit Ausreißern")

st.markdown(
    "Interaktive Version des Notebooks `Simple_Plot_a.ipynb`. "
    "Daten hochladen oder synthetisch erzeugen und Ausreißer-Anteil anpassen."
)

# -------------------- Daten --------------------
st.sidebar.header("Daten")
src = st.sidebar.radio("Quelle", ["Synthetisch", "CSV hochladen"])

if src == "Synthetisch":
    n = st.sidebar.slider("Datenpunkte", 50, 5000, 500)
    mu = st.sidebar.number_input("Mittelwert", value=80.0)
    sigma = st.sidebar.number_input("Std", value=8.0, min_value=0.0)
    seed = st.sidebar.number_input("Seed", value=42, step=1)
    rng = np.random.default_rng(int(seed))
    times = pd.date_range("2024-01-01", periods=n, freq="min")
    df = pd.DataFrame({"time": times, "heartrate": rng.normal(mu, sigma, n)})
    value_col = "heartrate"
    time_col = "time"
else:
    uploaded = st.sidebar.file_uploader("CSV", type=["csv"])
    if uploaded is None:
        st.info("Bitte CSV hochladen.")
        st.stop()
    df = pd.read_csv(uploaded)
    value_col = st.sidebar.selectbox(
        "Wertespalte", df.select_dtypes(include=np.number).columns
    )
    time_choice = st.sidebar.selectbox("Zeitspalte (optional)", ["(keine)"] + list(df.columns))
    time_col = None if time_choice == "(keine)" else time_choice
    if time_col is not None:
        try:
            df[time_col] = pd.to_datetime(df[time_col])
        except Exception:
            st.warning(f"'{time_col}' nicht in Datetime umwandelbar.")

# -------------------- Ausreißer injizieren --------------------
st.sidebar.header("Ausreißer einfügen")
pct = st.sidebar.slider("Anteil [%]", 0.0, 20.0, 3.0, 0.5)
low_val = st.sidebar.number_input("Niedriger Wert", value=0.0)
high_val = st.sidebar.number_input("Hoher Wert", value=700.0)
inj_seed = st.sidebar.number_input("Inject Seed", value=1, step=1)

sample = df[value_col].copy().astype(float)
n_inject = int(len(sample) * pct / 100)
if n_inject > 0:
    rng_i = np.random.default_rng(int(inj_seed))
    idx = rng_i.choice(sample.index, size=n_inject, replace=False)
    sample.loc[idx] = rng_i.choice([low_val, high_val], size=n_inject)

# -------------------- Styling --------------------
st.sidebar.header("Styling")
color = st.sidebar.color_picker("Linienfarbe", "#d62728")
fig_w = st.sidebar.slider("Breite", 4, 16, 10)
fig_h = st.sidebar.slider("Höhe", 3, 10, 5)
title = st.sidebar.text_input("Titel", value="Liniendiagramm der Herzrate über die Zeit")
xlabel = st.sidebar.text_input("X-Achse", value="Zeit" if time_col else "Index")
ylabel = st.sidebar.text_input("Y-Achse", value=value_col)

# -------------------- Plot --------------------
fig, ax = plt.subplots(figsize=(fig_w, fig_h))
x = df[time_col] if time_col is not None else np.arange(len(sample))
sns.lineplot(x=x, y=sample, color=color, ax=ax)
ax.set_xlabel(xlabel)
ax.set_ylabel(ylabel)
ax.set_title(title)
st.pyplot(fig)

st.subheader("Datenvorschau")
st.dataframe(
    pd.DataFrame({**({time_col: x} if time_col else {"index": x}), value_col: sample}).head(50),
    use_container_width=True,
)
