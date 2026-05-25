import streamlit as st

st.set_page_config(
    page_title="Data Literacy 2026",
    page_icon="📊",
    layout="centered",
)

st.title("📊 Data Literacy 2026 – Interaktive Notebooks")

st.markdown(
    """
    Willkommen! Diese Streamlit-App enthält für jedes Notebook im Ordner
    `notebooks/` eine eigene interaktive Seite. Alle Variablen, die in den
    Notebooks normalerweise im Code angepasst werden müssten, lassen sich
    hier per Slider, Eingabefeld oder Auswahlbox einstellen.

    **Seiten (links in der Seitenleiste):**

    1. **Cheatsheet** – Pandas-Grundlagen interaktiv durchklicken.
    2. **Math Functions** – Statistische Kennwerte (Mittelwert, Varianz,
       Schiefe, Kurtosis, T-Test …).
    3. **Outliers** – Ausreißer-Erkennung mit empirischer Regel und
       verschiedene Korrekturmethoden.
    4. **Plots** – Galerie unterschiedlicher Diagrammtypen mit
       konfigurierbaren Parametern.
    5. **Simple Plot** – Einfaches Liniendiagramm mit Ausreißern.

    **Daten:** Du kannst auf jeder Seite entweder Beispieldaten generieren
    lassen oder eine eigene CSV-Datei hochladen (z. B. `heart.csv`).
    """
)

st.markdown(
    "**BI-Vital Sensor:** Eigene Messungen kannst du mit der "
    "[BI-Vital Web-Toolbox](https://bivital.eu/docs/webtools/web-toolbox/) "
    "aufzeichnen und als CSV exportieren."
)

st.info("Wähle links eine Seite aus, um loszulegen.")
