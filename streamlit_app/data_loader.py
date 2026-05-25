from pathlib import Path

import pandas as pd
import streamlit as st

EXAMPLE_CSV = Path(__file__).resolve().parent.parent / "example_data" / "example0.csv"


@st.cache_data
def load_example_csv(path: str | Path = EXAMPLE_CSV) -> pd.DataFrame:
    """BI-Vital CSV einlesen (2 Metadaten-Zeilen überspringen) und auf `time`/`heartrate` säubern."""
    df = pd.read_csv(path, skiprows=2, skipinitialspace=True)
    df = df.rename(columns={"Time [s]": "time", "Heartrate [bpm]": "heartrate"})
    df["heartrate"] = pd.to_numeric(df["heartrate"], errors="coerce")
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df = df.dropna(subset=["heartrate", "time"]).reset_index(drop=True)
    return df
