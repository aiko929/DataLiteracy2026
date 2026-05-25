import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_loader import load_example_csv  # noqa: E402

st.set_page_config(page_title="Simple Plot B", page_icon="📈", layout="wide")
st.title("📈 Einfaches Liniendiagramm")

st.caption(
    "Interaktive Version des Notebooks `Simple_Plot_b.ipynb`. "
    "Datenquelle in der Sidebar, Plot-Optionen direkt neben dem Plot."
)

# ==================== Sidebar: Daten ====================
st.sidebar.header("Daten")
src = st.sidebar.radio("Quelle", ["Beispiel-CSV (BI-Vital)", "Synthetisch", "CSV hochladen"])

if src == "Beispiel-CSV (BI-Vital)":
    df = load_example_csv()
    value_col = "heartrate"
    time_col = "time"
elif src == "Synthetisch":
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
    df = pd.read_csv(uploaded, skiprows=2)
    df = df.apply(pd.to_numeric, errors='coerce')
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

# ==================== Hauptbereich: Optionen | Plot ====================
opt_col, plot_col = st.columns([1, 3], gap="large")

with opt_col:
    st.subheader("Styling")
    color = st.color_picker("Linienfarbe", "#d62728")
    fig_w = st.slider("Breite", 4, 16, 10)
    fig_h = st.slider("Höhe", 3, 10, 5)
    title = st.text_input("Titel", value="Liniendiagramm der Herzrate über die Zeit")
    xlabel = st.text_input("X-Achse", value="Zeit" if time_col else "Index")
    ylabel = st.text_input("Y-Achse", value=value_col)

sample = df[value_col].astype(float)

with plot_col:
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    x = df[time_col] if time_col is not None else np.arange(len(sample))
    sns.lineplot(x=x, y=sample, color=color, ax=ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    st.pyplot(fig, use_container_width=True)

with st.expander("Datenvorschau"):
    st.dataframe(
        pd.DataFrame({**({time_col: x} if time_col else {"index": x}), value_col: sample}).head(50),
        use_container_width=True,
    )
