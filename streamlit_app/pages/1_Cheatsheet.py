import io

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Cheatsheet", page_icon="📒", layout="wide")
st.title("📒 Pandas Cheatsheet (interaktiv)")

st.markdown(
    "Spiele die wichtigsten Pandas-Operationen direkt am Beispiel-DataFrame durch. "
    "Du kannst den Beispieldatensatz selbst zusammenstellen oder eine eigene CSV/Excel hochladen."
)

# -------------------- Daten laden --------------------
st.header("1. DataFrame erstellen")

source = st.radio(
    "Quelle des DataFrames",
    ["Manuell (Beispiel anpassen)", "CSV-Datei hochladen", "Excel-Datei hochladen"],
    horizontal=True,
)

df: pd.DataFrame | None = None

if source == "Manuell (Beispiel anpassen)":
    default_csv = "Name,Alter\nAnna,23\nBen,15\nBen,30\nChris,35"
    raw = st.text_area(
        "DataFrame als CSV-Text (Spalten kommagetrennt, Zeilen mit Zeilenumbruch)",
        value=default_csv,
        height=150,
    )
    try:
        df = pd.read_csv(io.StringIO(raw))
    except Exception as exc:
        st.error(f"Konnte den Text nicht als CSV interpretieren: {exc}")

elif source == "CSV-Datei hochladen":
    sep = st.text_input("Trennzeichen", value=",")
    uploaded = st.file_uploader("CSV-Datei", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded, sep=sep)

else:
    uploaded = st.file_uploader("Excel-Datei", type=["xlsx", "xls"])
    if uploaded is not None:
        df = pd.read_excel(uploaded)

if df is None or df.empty:
    st.info("Bitte zunächst Daten bereitstellen.")
    st.stop()

st.subheader("Aktueller DataFrame")
st.dataframe(df, use_container_width=True)

# -------------------- Erste Einblicke --------------------
st.header("2. Erste Einblicke")

col1, col2 = st.columns(2)
with col1:
    head_n = st.slider("df.head(n)", 1, max(1, len(df)), min(5, len(df)))
    st.write("`df.head(n)`")
    st.dataframe(df.head(head_n), use_container_width=True)
with col2:
    tail_n = st.slider("df.tail(n)", 1, max(1, len(df)), min(5, len(df)))
    st.write("`df.tail(n)`")
    st.dataframe(df.tail(tail_n), use_container_width=True)

with st.expander("df.info() / df.describe() / df.shape …"):
    buf = io.StringIO()
    df.info(buf=buf)
    st.text(buf.getvalue())
    st.write("`df.describe()`")
    st.dataframe(df.describe(include="all"), use_container_width=True)
    st.write(f"`df.shape` = {df.shape}")
    st.write(f"`df.columns` = {list(df.columns)}")
    st.write("`df.dtypes`")
    st.write(df.dtypes)
    st.write("`df.nunique()`")
    st.write(df.nunique())

# -------------------- Spalten auswählen --------------------
st.header("3. Spalten & Zeilen auswählen")

selected_cols = st.multiselect("Spalten auswählen", list(df.columns), default=list(df.columns))
if selected_cols:
    st.dataframe(df[selected_cols], use_container_width=True)

row_range = st.slider("Zeilen (iloc) Bereich", 0, len(df), (0, min(3, len(df))))
st.write(f"`df.iloc[{row_range[0]}:{row_range[1]}]`")
st.dataframe(df.iloc[row_range[0]:row_range[1]], use_container_width=True)

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
if numeric_cols:
    filter_col = st.selectbox("Filterspalte (numerisch)", numeric_cols)
    op = st.selectbox("Vergleich", [">", ">=", "<", "<=", "==", "!="])
    threshold = st.number_input(
        "Schwellenwert", value=float(df[filter_col].median())
    )
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

# -------------------- Bearbeiten --------------------
st.header("4. Bearbeiten")

if numeric_cols:
    edit_col = st.selectbox("Spalte verändern", numeric_cols, key="edit")
    offset = st.number_input("Wert addieren", value=1.0)
    factor = st.number_input("Mit Faktor multiplizieren", value=1.0)
    new_name = st.text_input("Neue Spalte umbenennen in (leer = unverändert)", value="")
    edited = df.copy()
    edited[edit_col] = (edited[edit_col] + offset) * factor
    if new_name:
        edited.rename(columns={edit_col: new_name}, inplace=True)
    st.dataframe(edited, use_container_width=True)

sort_col = st.selectbox("Nach Spalte sortieren", df.columns)
ascending = st.checkbox("Aufsteigend", value=True)
st.dataframe(df.sort_values(sort_col, ascending=ascending), use_container_width=True)

# -------------------- Fehlende Werte --------------------
st.header("5. Fehlende Werte")
st.write("`df.isnull().sum()`")
st.write(df.isnull().sum())
strategy = st.selectbox(
    "Strategie",
    ["nichts tun", "dropna", "fillna mit Wert", "fillna mit Mittelwert (numerisch)"],
)
if strategy == "dropna":
    st.dataframe(df.dropna(), use_container_width=True)
elif strategy == "fillna mit Wert":
    val = st.text_input("Wert", value="Unbekannt")
    st.dataframe(df.fillna(val), use_container_width=True)
elif strategy == "fillna mit Mittelwert (numerisch)":
    filled = df.copy()
    for c in numeric_cols:
        filled[c] = filled[c].fillna(filled[c].mean())
    st.dataframe(filled, use_container_width=True)

# -------------------- Gruppieren --------------------
st.header("6. Gruppieren & aggregieren")
if numeric_cols and len(df.columns) >= 2:
    group_col = st.selectbox("Gruppieren nach", df.columns, key="group")
    agg_col = st.selectbox("Aggregieren auf", numeric_cols, key="agg")
    agg_fn = st.selectbox("Aggregatfunktion", ["mean", "sum", "max", "min", "count"])
    st.dataframe(df.groupby(group_col)[agg_col].agg(agg_fn), use_container_width=True)

# -------------------- Speichern --------------------
st.header("7. Speichern")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Als CSV herunterladen", csv, "output.csv", "text/csv")
