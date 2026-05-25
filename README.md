# Data Literacy 2026

Interaktive Lehrmaterialien zum Kurs **Data Literacy 2026** – bestehend aus Jupyter-Notebooks und einer begleitenden Streamlit-App, mit der sich alle relevanten Parameter ohne Code-Anpassung per Slider, Eingabefeld oder Auswahlbox erkunden lassen.

## Inhalt

- **`notebooks/`** – Jupyter-Notebooks zum Mitmachen (auch in Google Colab lauffähig):
  - `Cheatsheet_Colab.ipynb` – Pandas-Grundlagen
  - `Math_Functions.ipynb` – statistische Kennwerte (Mittelwert, Varianz, Schiefe, Kurtosis, T-Test, …)
  - `Outliers.ipynb` – Ausreißer-Erkennung und Korrekturmethoden
  - `Plots.ipynb` – Galerie unterschiedlicher Diagrammtypen
  - `Simple_Plot_a.ipynb`, `Simple_Plot_b.ipynb` – einfache Liniendiagramme mit Ausreißern
- **`streamlit_app/`** – Streamlit-App mit einer interaktiven Seite pro Notebook
- **`example_data/`** – Beispiel-CSV-Dateien (BI-Vital Sensor-Logs)

## Voraussetzungen

- Python 3.11 oder 3.12
- Abhängigkeiten: `streamlit`, `pandas`, `numpy`, `matplotlib`, `scipy`

```bash
pip install streamlit pandas numpy matplotlib scipy
```

## Streamlit-App starten

Aus dem Projektverzeichnis:

```bash
streamlit run streamlit_app/app.py
```

In der Seitenleiste lassen sich die einzelnen Seiten (Cheatsheet, Math Functions, Outliers, Plots, Simple Plot) auswählen. Auf jeder Seite können entweder Beispieldaten generiert, die mitgelieferte BI-Vital-CSV verwendet oder eine eigene CSV-Datei hochgeladen werden.

## Notebooks verwenden

Die Notebooks im Ordner `notebooks/` lassen sich lokal mit Jupyter oder direkt in Google Colab öffnen.

## Beispieldaten

`example_data/example0.csv` enthält einen BI-Vital-Sensor-Log mit Herzfrequenz, RR-Intervallen, Temperatur, Luftfeuchte, Druck und Lageinformationen. Das Format hat zwei Metadaten-Kopfzeilen; das Einlesen ist in [streamlit_app/data_loader.py](streamlit_app/data_loader.py) gekapselt.
