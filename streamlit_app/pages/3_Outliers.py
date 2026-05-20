import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Outliers", page_icon="🚨", layout="wide")
st.title("🚨 Ausreißer & empirische Regel")

st.markdown(
    "Interaktive Version des Notebooks `Outliers.ipynb`. "
    "Lade eine CSV hoch oder benutze synthetische Daten, dann probiere die "
    "Ausreißer-Erkennung und verschiedene Korrekturmethoden aus."
)

# -------------------- Daten --------------------
st.sidebar.header("Daten")
src = st.sidebar.radio("Quelle", ["Synthetisch", "CSV hochladen"])

if src == "Synthetisch":
    n = st.sidebar.slider("Anzahl Datenpunkte", 50, 5000, 500)
    mu = st.sidebar.number_input("Mittelwert", value=80.0)
    sigma = st.sidebar.number_input("Standardabweichung", value=8.0, min_value=0.0)
    seed = st.sidebar.number_input("Seed", value=42, step=1)
    rng = np.random.default_rng(int(seed))
    values = rng.normal(mu, sigma, n)
    times = pd.date_range("2024-01-01", periods=n, freq="min")
    df = pd.DataFrame({"time": times, "heartrate": values})
    value_col = "heartrate"
    time_col = "time"
else:
    uploaded = st.sidebar.file_uploader("CSV", type=["csv"])
    if uploaded is None:
        st.info("Bitte CSV hochladen.")
        st.stop()
    df = pd.read_csv(uploaded)
    value_col = st.sidebar.selectbox(
        "Wertespalte",
        df.select_dtypes(include=np.number).columns,
    )
    time_col = st.sidebar.selectbox(
        "Zeitspalte (optional)", ["(keine)"] + list(df.columns)
    )
    if time_col == "(keine)":
        time_col = None
    df[value_col] = df[value_col].astype(float)
    if time_col is not None:
        try:
            df[time_col] = pd.to_datetime(df[time_col])
        except Exception:
            st.warning(f"Konnte Spalte '{time_col}' nicht in Datetime umwandeln.")

# Künstliche Ausreißer einbauen
st.sidebar.header("Ausreißer einfügen")
inject = st.sidebar.slider("Anteil künstlicher Ausreißer [%]", 0.0, 20.0, 3.0, 0.5)
low_val = st.sidebar.number_input("Niedriger Ausreißerwert", value=0.0)
high_val = st.sidebar.number_input("Hoher Ausreißerwert", value=700.0)
inject_seed = st.sidebar.number_input("Inject Seed", value=1, step=1)

sample = df[value_col].copy()
n_inject = int(len(sample) * inject / 100)
if n_inject > 0:
    rng_i = np.random.default_rng(int(inject_seed))
    idxs = rng_i.choice(sample.index, size=n_inject, replace=False)
    sample.loc[idxs] = rng_i.choice([low_val, high_val], size=n_inject)
df[value_col] = sample

st.subheader("Daten mit eingefügten Ausreißern")
st.dataframe(df.head(), use_container_width=True)

# -------------------- Empirische Regel --------------------
st.header("Empirische Regel")
mean = df[value_col].mean()
std = df[value_col].std()
c1, c2 = st.columns(2)
c1.metric("Mittelwert", f"{mean:.3f}")
c2.metric("Standardabweichung", f"{std:.3f}")

k = st.slider("Anzahl Standardabweichungen k", 1, 5, 3)
lower = mean - k * std
upper = mean + k * std
mask = (df[value_col] > lower) & (df[value_col] < upper)
pct = mask.mean() * 100
st.write(
    f"**{pct:.2f} %** der Werte liegen zwischen **{lower:.2f}** und **{upper:.2f}** "
    f"(±{k}·σ)."
)
st.caption(
    "Faustregel Normalverteilung: 1σ ≈ 68 %, 2σ ≈ 95 %, 3σ ≈ 99,7 %. "
    "Werte außerhalb von ±3σ gelten typischerweise als Ausreißer."
)

# -------------------- Korrekturmethoden --------------------
st.header("Korrektur der Ausreißer")
method = st.selectbox(
    "Methode",
    [
        "Top/Bottom-Coding (clip auf ±kσ)",
        "Ersatz durch Mittelwert",
        "Lineare Interpolation",
    ],
)

if method == "Top/Bottom-Coding (clip auf ±kσ)":
    corrected = df[value_col].clip(lower=lower, upper=upper)
elif method == "Ersatz durch Mittelwert":
    corrected = df[value_col].apply(lambda x: mean if x < lower or x > upper else x)
else:
    tmp = df[value_col].copy()
    tmp.loc[(tmp < lower) | (tmp > upper)] = np.nan
    corrected = tmp.interpolate()

df["corrected"] = corrected

# -------------------- Plots --------------------
st.header("Visualisierung")
color_orig = st.color_picker("Farbe Original", "#d62728")
color_corr = st.color_picker("Farbe Korrigiert", "#1f77b4")
figsize_w = st.slider("Plotbreite", 4, 16, 10)
figsize_h = st.slider("Plothöhe", 3, 10, 4)

x = df[time_col] if time_col is not None else np.arange(len(df))

fig, ax = plt.subplots(figsize=(figsize_w, figsize_h))
sns.lineplot(x=x, y=df[value_col], color=color_orig, ax=ax, label="Original")
ax.axhline(lower, color="grey", linestyle="--", alpha=0.7)
ax.axhline(upper, color="grey", linestyle="--", alpha=0.7)
ax.set_xlabel("Zeit" if time_col else "Index")
ax.set_ylabel(value_col)
ax.set_title("Original mit ±kσ-Grenzen")
ax.legend()
st.pyplot(fig)

fig2, ax2 = plt.subplots(figsize=(figsize_w, figsize_h))
sns.lineplot(x=x, y=df["corrected"], color=color_corr, ax=ax2, label="Korrigiert")
ax2.set_xlabel("Zeit" if time_col else "Index")
ax2.set_ylabel(value_col)
ax2.set_title(f"Korrigiert ({method})")
ax2.legend()
st.pyplot(fig2)

st.download_button(
    "Korrigierte Daten als CSV herunterladen",
    df.to_csv(index=False).encode("utf-8"),
    "outliers_corrected.csv",
    "text/csv",
)
