import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_loader import load_example_csv  # noqa: E402

st.set_page_config(page_title="Cheatsheet", page_icon="📒", layout="wide")
st.title("📒 Pandas Cheatsheet (interaktiv)")

st.caption(
    "Spiele die wichtigsten Pandas-Operationen direkt am Beispiel-DataFrame durch. "
    "Eingaben links, Ergebnisse rechts."
)

# ==================== Sidebar: Datenquelle ====================
st.sidebar.header("DataFrame erstellen")

source = st.sidebar.radio(
    "Quelle",
    [
        "Manuell (Beispiel anpassen)",
        "Beispiel-CSV (BI-Vital)",
        "CSV-Datei hochladen",
    ],
)

df: pd.DataFrame | None = None

if source == "Beispiel-CSV (BI-Vital)":
    df = load_example_csv()
elif source == "Manuell (Beispiel anpassen)":
    default_csv = "Name,Alter\nAnna,23\nBen,15\nBen,30\nChris,35"
    raw = st.sidebar.text_area(
        "DataFrame als CSV-Text",
        value=default_csv,
        height=150,
    )
    try:
        df = pd.read_csv(io.StringIO(raw))
    except Exception as exc:
        st.error(f"Konnte den Text nicht als CSV interpretieren: {exc}")

elif source == "CSV-Datei hochladen":
    sep = st.sidebar.text_input("Trennzeichen", value=",")
    uploaded = st.sidebar.file_uploader("CSV-Datei", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded, sep=sep, skiprows=2)
        df = df.apply(pd.to_numeric, errors='coerce')

if df is None or df.empty:
    st.info("Bitte zunächst Daten in der Sidebar bereitstellen.")
    st.stop()

st.subheader("Aktueller DataFrame")
st.dataframe(df, use_container_width=True)

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

# ==================== Block: Erste Einblicke ====================
st.divider()
st.header("1. Erste Einblicke")
opt, res = st.columns([1, 2], gap="large")
with opt:
    head_n = st.slider("df.head(n)", 1, max(1, len(df)), min(5, len(df)))
    tail_n = st.slider("df.tail(n)", 1, max(1, len(df)), min(5, len(df)))
with res:
    c1, c2 = st.columns(2)
    with c1:
        st.write("`df.head(n)`")
        st.dataframe(df.head(head_n), use_container_width=True)
    with c2:
        st.write("`df.tail(n)`")
        st.dataframe(df.tail(tail_n), use_container_width=True)

with st.expander("df.describe() / df.shape …"):
    st.write("`df.describe()`")
    st.dataframe(df.describe(include="all"), use_container_width=True)
    st.write(f"`df.shape` = {df.shape}")
    st.write(f"`df.columns` = {list(df.columns)}")
    st.write("`df.dtypes`")
    st.write(df.dtypes)
    st.write("`df.nunique()`")
    st.write(df.nunique())

# ==================== Block: Auswählen ====================
st.divider()
st.header("2. Spalten & Zeilen auswählen")
opt, res = st.columns([1, 2], gap="large")
with opt:
    selected_cols = st.multiselect("Spalten", list(df.columns), default=list(df.columns))
    row_range = st.slider("iloc Zeilenbereich", 0, len(df), (0, min(3, len(df))))
    if numeric_cols:
        filter_col = st.selectbox("Filterspalte (numerisch)", numeric_cols)
        op = st.selectbox("Vergleich", [">", ">=", "<", "<=", "==", "!="])
        threshold = st.number_input(
            "Schwellenwert", value=float(df[filter_col].median())
        )
with res:
    if selected_cols:
        st.write("Spaltenauswahl")
        st.dataframe(df[selected_cols], use_container_width=True)
    st.write(f"`df.iloc[{row_range[0]}:{row_range[1]}]`")
    st.dataframe(df.iloc[row_range[0]:row_range[1]], use_container_width=True)
    if numeric_cols:
        expr_map = {
            ">": df[filter_col] > threshold,
            ">=": df[filter_col] >= threshold,
            "<": df[filter_col] < threshold,
            "<=": df[filter_col] <= threshold,
            "==": df[filter_col] == threshold,
            "!=": df[filter_col] != threshold,
        }
        st.write(f"`df.loc[df['{filter_col}'] {op} {threshold}]`")
        st.dataframe(df.loc[expr_map[op]], use_container_width=True)

# ==================== Block: Bearbeiten ====================
st.divider()
st.header("3. Bearbeiten")
opt, res = st.columns([1, 2], gap="large")
with opt:
    if numeric_cols:
        edit_col = st.selectbox("Spalte verändern", numeric_cols, key="edit")
        offset = st.number_input("Wert addieren", value=1.0)
        factor = st.number_input("Mit Faktor multiplizieren", value=1.0)
        new_name = st.text_input("Spalte umbenennen (leer = unverändert)", value="")
    sort_col = st.selectbox("Sortierspalte", df.columns)
    ascending = st.checkbox("Aufsteigend", value=True)
with res:
    if numeric_cols:
        edited = df.copy()
        edited[edit_col] = (edited[edit_col] + offset) * factor
        if new_name:
            edited.rename(columns={edit_col: new_name}, inplace=True)
        st.write("Bearbeiteter DataFrame")
        st.dataframe(edited, use_container_width=True)
    st.write(f"Sortiert nach `{sort_col}`")
    st.dataframe(df.sort_values(sort_col, ascending=ascending), use_container_width=True)

# ==================== Block: Fehlende Werte ====================
st.divider()
st.header("4. Fehlende Werte")
opt, res = st.columns([1, 2], gap="large")
with opt:
    strategy = st.selectbox(
        "Strategie",
        ["nichts tun", "dropna", "fillna mit Wert", "fillna mit Mittelwert (numerisch)"],
    )
    fill_value = None
    if strategy == "fillna mit Wert":
        fill_value = st.text_input("Wert", value="Unbekannt")
with res:
    st.write("`df.isnull().sum()`")
    st.write(df.isnull().sum())
    if strategy == "dropna":
        st.dataframe(df.dropna(), use_container_width=True)
    elif strategy == "fillna mit Wert":
        st.dataframe(df.fillna(fill_value), use_container_width=True)
    elif strategy == "fillna mit Mittelwert (numerisch)":
        filled = df.copy()
        for c in numeric_cols:
            filled[c] = filled[c].fillna(filled[c].mean())
        st.dataframe(filled, use_container_width=True)

# ==================== Block: Gruppieren ====================
st.divider()
st.header("5. Gruppieren & aggregieren")
opt, res = st.columns([1, 2], gap="large")
with opt:
    if numeric_cols and len(df.columns) >= 2:
        group_col = st.selectbox("Gruppieren nach", df.columns, key="group")
        agg_col = st.selectbox("Aggregieren auf", numeric_cols, key="agg")
        agg_fn = st.selectbox("Aggregatfunktion", ["mean", "sum", "max", "min", "count"])
with res:
    if numeric_cols and len(df.columns) >= 2:
        st.dataframe(df.groupby(group_col)[agg_col].agg(agg_fn), use_container_width=True)

# ==================== Block: Speichern ====================
st.divider()
st.header("6. Speichern")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Als CSV herunterladen", csv, "output.csv", "text/csv")
