# Netflix Insights Dashboard

A Streamlit dashboard for exploring the sample Netflix viewing dataset. Filter records by region, subscription plan, category, and watch date, then compare revenue, ratings, and viewing activity.

## Features

- Summary metrics for customers, monthly revenue, average rating, and watch time
- Revenue by region and category
- Average rating by subscription plan
- Monthly revenue trend
- Content type distribution and most-watched titles
- Filtered records in an expandable data table

## Requirements

- Python 3
- Streamlit
- pandas
- Altair

## Run locally

From the project directory, create and activate a virtual environment, install the dependencies, and start the app:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install streamlit pandas altair
python -m streamlit run neflix_proj.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## Project files

- `neflix_proj.py` - Streamlit dashboard
- `netflix.csv` - sample data loaded by the dashboard

The CSV is expected to be in the same directory as the Python file. The included sample dataset is synthetic.
