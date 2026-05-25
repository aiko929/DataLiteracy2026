import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import kurtosis, skew, ttest_ind

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_loader import load_example_csv  # noqa: E402

st.set_page_config(page_title="Math Functions", page_icon="🧮", layout="wide")
st.title("🧮 Statistische Kennwerte")

st.caption(
    "Interaktive Version des Notebooks `Math_Functions.ipynb`. "
    "Datenquelle in der Sidebar, Optionen und Ergebnisse nebeneinander."
)

# ==================== Sidebar: Datenquelle ====================
st.sidebar.header("Datenquelle")
mode = st.sidebar.radio(
    "Stichprobe sample",
    ["Beispiel-CSV (BI-Vital, heartrate)", "Manuelle Eingabe", "Zufallsgenerator"],
)

sample: np.ndarray | pd.Series

if mode == "Beispiel-CSV (BI-Vital, heartrate)":
    sample = load_example_csv()["heartrate"].to_numpy()
elif mode == "Manuelle Eingabe":
    txt = st.sidebar.text_input(
        "Werte (Komma-getrennt)", value="1,2,3,4,5,6,7,8,9"
    )
    try:
        sample = np.array([float(v.strip()) for v in txt.split(",") if v.strip() != ""])
    except ValueError:
        st.error("Bitte nur Zahlen, durch Kommata getrennt.")
        st.stop()

elif mode == "Zufallsgenerator":
    n = st.sidebar.slider("Anzahl Werte", 5, 5000, 100)
    mu = st.sidebar.number_input("Mittelwert µ", value=70.0)
    sigma = st.sidebar.number_input("Standardabweichung σ", value=10.0, min_value=0.0)
    seed = st.sidebar.number_input("Random Seed", value=42, step=1)
    rng = np.random.default_rng(int(seed))
    sample = rng.normal(mu, sigma, n)


def get_mode(x):
    values, counts = np.unique(x, return_counts=True)
    return values[np.argmax(counts)]


# ==================== Block 1: Kennzahlen ====================
opt_col, res_col = st.columns([1, 2], gap="large")

with opt_col:
    st.subheader("Optionen Kennzahlen")
    ddof = st.slider("Freiheitsgrad (ddof) für Varianz/Std", 0, 1, 1)
    qs = st.multiselect(
        "Quantile (%) auswählen",
        [5, 10, 25, 33, 50, 66, 75, 90, 95, 99],
        default=[25, 50, 75],
    )
    fisher = st.checkbox("Fisher-Definition Kurtosis (Excess)", value=True)
    bias = st.checkbox("Biased estimator (Schiefe/Kurtosis)", value=True)

with res_col:
    st.subheader("Statistische Kennwerte")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mittelwert", f"{np.mean(sample):.4f}")
    c2.metric(f"Varianz", f"{np.var(sample, ddof=ddof):.4f}")
    c3.metric(f"Std", f"{np.std(sample, ddof=ddof):.4f}")
    c4.metric("Median", f"{np.median(sample):.4f}")

    c5, c6, c7 = st.columns(3)
    c5.metric("Modus", f"{get_mode(sample):.4f}")
    c6.metric("Wertebereich", f"{np.ptp(sample):.4f}")
    c7.metric("n", f"{len(sample)}")

    cA, cB = st.columns(2)
    cA.metric("Kurtosis", f"{kurtosis(sample, fisher=fisher, bias=bias):.4f}")
    cB.metric("Schiefe", f"{skew(sample, bias=bias):.4f}")

    if qs:
        quantiles = np.percentile(sample, qs)
        st.table(pd.DataFrame({"Quantil [%]": qs, "Wert": quantiles}))

# ==================== Block 2: T-Test ====================
st.divider()
st.header("T-Test gegen zweite Stichprobe")

t_opt, t_res = st.columns([1, 2], gap="large")

with t_opt:
    st.subheader("Zweite Stichprobe")
    mode2 = st.radio("Quelle", ["Zufall (normal)", "Manuelle Eingabe"])
    if mode2 == "Zufall (normal)":
        n2 = st.slider("n", 5, 5000, 100, key="n2")
        mu2 = st.number_input("µ2", value=5.0)
        sigma2 = st.number_input("σ2", value=2.0, min_value=0.0)
        seed2 = st.number_input("Random Seed 2", value=0, step=1)
        rng2 = np.random.default_rng(int(seed2))
        sample2 = rng2.normal(mu2, sigma2, n2)
    else:
        txt2 = st.text_input("Werte (Komma-getrennt)", value="4,5,6,5,4,5,6,7")
        try:
            sample2 = np.array([float(v.strip()) for v in txt2.split(",") if v.strip()])
        except ValueError:
            st.error("Bitte Zahlen.")
            st.stop()
    equal_var = st.checkbox("equal_var (Student-t statt Welch-t)", value=True)

with t_res:
    st.subheader("Ergebnis")
    result = ttest_ind(sample, sample2, equal_var=equal_var)
    c1, c2, c3 = st.columns(3)
    c1.metric("t-Statistik", f"{result.statistic:.4f}")
    c2.metric("p-Wert", f"{result.pvalue:.4f}")
    c3.metric("df", f"{getattr(result, 'df', float('nan')):.2f}")

    if result.pvalue < 0.05:
        st.success("p < 0.05 – Unterschied der Mittelwerte ist statistisch signifikant.")
    else:
        st.info("p ≥ 0.05 – kein signifikanter Unterschied der Mittelwerte.")

with st.expander("Stichprobenvorschau"):
    st.write(f"sample: n = {len(sample)}")
    st.dataframe(pd.DataFrame({"sample": sample}).head(20), use_container_width=True)
