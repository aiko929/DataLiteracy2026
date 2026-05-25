import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_loader import load_example_csv  # noqa: E402

st.set_page_config(page_title="Plots", page_icon="📈", layout="wide")
st.title("📈 Plot-Galerie")

st.caption(
    "Interaktive Version des Notebooks `Plots.ipynb`. "
    "Daten- und Stiloptionen sind in der Sidebar, plotspezifische Optionen "
    "stehen direkt neben dem Plot."
)

# ==================== Sidebar: Daten & globales Styling ====================
st.sidebar.header("Daten")
src = st.sidebar.radio(
    "Quelle",
    ["Synthetisch (zwei Stichproben)"], # Currently Hidden: "CSV hochladen", "Beispiel-CSV (BI-Vital)"
)

if src == "Beispiel-CSV (BI-Vital)":
    _df = load_example_csv()
    sample = _df["heartrate"].to_numpy()
    time = _df["time"].to_numpy()
    sample2 = np.full_like(sample, np.nan, dtype=float)
    age = np.arange(len(sample))
elif src == "Synthetisch (zwei Stichproben)":
    n = st.sidebar.slider("Anzahl Werte pro Sample", 10, 2000, 100)
    seed = st.sidebar.number_input("Seed", value=42, step=1)
    rng = np.random.default_rng(int(seed))

    st.sidebar.markdown("**Sample 1**")
    mu1 = st.sidebar.number_input("µ1", value=70.0)
    sd1 = st.sidebar.number_input("σ1", value=10.0, min_value=0.0)

    st.sidebar.markdown("**Sample 2**")
    mu2 = st.sidebar.number_input("µ2", value=75.0)
    sd2 = st.sidebar.number_input("σ2", value=12.0, min_value=0.0)

    st.sidebar.markdown("**Alter (Scatter)**")
    age_min = st.sidebar.number_input("Alter min", value=20)
    age_max = st.sidebar.number_input("Alter max", value=80)

    sample = rng.normal(mu1, sd1, n)
    sample2 = rng.normal(mu2, sd2, n)
    time = np.arange(1, n + 1)
    age = rng.integers(int(age_min), int(age_max) + 1, n)
else:
    uploaded = st.sidebar.file_uploader("CSV", type=["csv"])
    if uploaded is None:
        st.info("Bitte CSV hochladen.")
        st.stop()
    df = pd.read_csv(uploaded)
    numcols = df.select_dtypes(include=np.number).columns.tolist()
    sample = df[st.sidebar.selectbox("Sample 1 Spalte", numcols)].to_numpy()
    sample2_col = st.sidebar.selectbox("Sample 2 Spalte (optional)", ["(keine)"] + numcols)
    if sample2_col != "(keine)":
        sample2 = df[sample2_col].to_numpy()
    else:
        sample2 = np.full_like(sample, np.nan, dtype=float)
    time = np.arange(1, len(sample) + 1)
    age_col = st.sidebar.selectbox("Alter Spalte (optional)", ["(keine)"] + numcols)
    age = df[age_col].to_numpy() if age_col != "(keine)" else np.arange(len(sample))

st.sidebar.header("Globales Styling")
fig_w = st.sidebar.slider("Plotbreite", 4, 16, 8)
fig_h = st.sidebar.slider("Plothöhe", 3, 12, 5)
grid = st.sidebar.checkbox("Gitter", value=True)
color1 = st.sidebar.color_picker("Farbe 1", "#87CEEB")
color2 = st.sidebar.color_picker("Farbe 2", "#FFA500")

# ==================== Hauptbereich: Optionen | Plot ====================
plot_type = st.selectbox(
    "Plot-Typ",
    [
        "Tabellenansicht (zwei Datensätze)",
        "Histogramm",
        "Histogramm (zwei Datensätze)",
        "Dichteplot (KDE)",
        "Boxplot",
        "Boxplot (zwei Datensätze)",
        "Violinplot",
        "Violinplot (zwei Datensätze)",
        "Scatterplot (Alter vs. Werte)",
        "Scatterplot (zwei Datensätze)",
        "Lineplot",
        "Lineplot (zwei Datensätze)",
        "Heatmap (Korrelationsmatrix)",
        "Balkendiagramm (Mittelwerte)",
        "Gruppiertes Balkendiagramm",
        "Kreisdiagramm",
        "Stacked Area",
        "Stemplot",
        "Stripplot",
    ],
)

opt_col, plot_col = st.columns([1, 3], gap="large")

# Plot-Vorbereitung
fig, ax = plt.subplots(figsize=(fig_w, fig_h))

with opt_col:
    st.subheader("Optionen")
    title = st.text_input("Titel", value=plot_type)
    xlabel = st.text_input("X-Achse", value="")
    ylabel = st.text_input("Y-Achse", value="")


    if plot_type == "Tabellenansicht (zwei Datensätze)":
        df_table = pd.DataFrame({"Sample 1": sample, "Sample 2": sample2})
        st.dataframe(df_table)
    elif plot_type == "Histogramm":
        bins = st.slider("Bins", 5, 100, 15)
        ax.hist(sample, bins=bins, color=color1, edgecolor="black")
    elif plot_type == "Histogramm (zwei Datensätze)":
        bins = st.slider("Bins", 5, 100, 15)
        alpha = st.slider("Transparenz", 0.1, 1.0, 0.6)
        ax.hist(sample, bins=bins, color=color1, edgecolor="black", alpha=alpha, label="Sample 1")
        ax.hist(sample2, bins=bins, color=color2, edgecolor="black", alpha=alpha, label="Sample 2")
        ax.legend()
    elif plot_type == "Dichteplot (KDE)":
        fill = st.checkbox("Fläche füllen", value=True)
        sns.kdeplot(sample, fill=fill, color=color1, alpha=0.6, label="Sample 1", ax=ax)
        if not np.all(np.isnan(sample2)):
            sns.kdeplot(sample2, fill=fill, color=color2, alpha=0.6, label="Sample 2", ax=ax)
        ax.legend()
    elif plot_type == "Boxplot":
        sns.boxplot(x=sample, color=color1, ax=ax)
    elif plot_type == "Boxplot (zwei Datensätze)":
        sns.boxplot(data=[sample, sample2], palette=[color1, color2], ax=ax)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Sample 1", "Sample 2"])
    elif plot_type == "Violinplot":
        sns.violinplot(x=sample, color=color1, ax=ax)
    elif plot_type == "Violinplot (zwei Datensätze)":
        sns.violinplot(data=[sample, sample2], palette=[color1, color2], ax=ax)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Sample 1", "Sample 2"])
    elif plot_type == "Scatterplot (Alter vs. Werte)":
        sns.scatterplot(x=age, y=sample, color=color1, ax=ax)
    elif plot_type == "Scatterplot (zwei Datensätze)":
        sns.scatterplot(x=age, y=sample, color=color1, label="Sample 1", ax=ax)
        sns.scatterplot(x=age, y=sample2, color=color2, label="Sample 2", ax=ax)
        ax.legend()
    elif plot_type == "Lineplot":
        marker = st.text_input("Marker", value="o")
        sns.lineplot(x=time, y=sample, marker=marker, color=color1, ax=ax)
    elif plot_type == "Lineplot (zwei Datensätze)":
        marker = st.text_input("Marker", value="o")
        sns.lineplot(x=time, y=sample, marker=marker, color=color1, label="Sample 1", ax=ax)
        sns.lineplot(x=time, y=sample2, marker=marker, color=color2, label="Sample 2", ax=ax)
        ax.legend()
    elif plot_type == "Heatmap (Korrelationsmatrix)":
        cmap = st.selectbox(
            "Farbpalette",
            ["YlGnBu", "Blues", "coolwarm", "BuPu", "Greens", "Oranges", "Reds", "Purples", "YlOrBr"],
        )
        annot = st.checkbox("Werte anzeigen", value=True)
        data = pd.DataFrame(
            {
                "Alter": age,
                "Werte Sample 1": sample,
                "Werte Sample 2": sample2,
                "Zeit": time,
            }
        )
        sns.heatmap(data.corr(), annot=annot, cmap=cmap, fmt=".2f", ax=ax)
    elif plot_type == "Balkendiagramm (Mittelwerte)":
        means = [np.nanmean(sample), np.nanmean(sample2)]
        ax.bar(["Sample 1", "Sample 2"], means, color=[color1, color2])
    elif plot_type == "Gruppiertes Balkendiagramm":
        n_cat = st.slider("Anzahl Kategorien", 2, 10, 4)
        seed_b = st.number_input("Seed (Bars)", value=0, step=1)
        rng_b = np.random.default_rng(int(seed_b))
        cats = [chr(ord("A") + i) for i in range(n_cat)]
        v1 = rng_b.integers(10, 50, n_cat)
        v2 = rng_b.integers(10, 50, n_cat)
        x = np.arange(n_cat)
        w = 0.4
        ax.bar(x - w / 2, v1, w, color=color1, label="Gruppe 1")
        ax.bar(x + w / 2, v2, w, color=color2, label="Gruppe 2")
        ax.set_xticks(x)
        ax.set_xticklabels(cats)
        ax.legend()
    elif plot_type == "Kreisdiagramm":
        s1_factor = st.slider("Gewicht Sample 1", 0.1, 5.0, 2.0, 0.1)
        sizes = [len(sample) * s1_factor, len(sample2)]
        ax.pie(sizes, labels=["Sample 1", "Sample 2"], colors=[color1, color2], autopct="%1.1f%%", startangle=140)
    elif plot_type == "Stacked Area":
        alpha = st.slider("Transparenz", 0.1, 1.0, 0.6)
        ax.stackplot(time, sample, sample2, labels=["Sample 1", "Sample 2"], colors=[color1, color2], alpha=alpha)
        ax.legend()
    elif plot_type == "Stemplot":
        ax.stem(np.arange(1, len(sample) + 1), sample, linefmt="gray", markerfmt="o", basefmt=" ")
    elif plot_type == "Stripplot":
        jitter = st.checkbox("Jitter", value=True)
        sns.stripplot(data=[sample, sample2], palette=[color1, color2], jitter=jitter, ax=ax)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Sample 1", "Sample 2"])

ax.set_title(title)
if xlabel:
    ax.set_xlabel(xlabel)
if ylabel:
    ax.set_ylabel(ylabel)
if grid and plot_type not in ("Kreisdiagramm", "Heatmap (Korrelationsmatrix)"):
    ax.grid(True)

with plot_col:
    st.pyplot(fig, use_container_width=True)
