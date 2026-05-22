"""Data access layer for the Olist dashboard.

Primary source: BigQuery (runs the same SQL files in ``sql/analysis`` that the
analysis pipeline uses, so there is a single source of truth).
Fallback: the committed CSVs in ``results/tables`` — this keeps the dashboard
viewable and deployable even when BigQuery credentials are not configured.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

# Default project; overridable via st.secrets["gcp_project_id"].
DEFAULT_PROJECT_ID = "olist-analysis-project-495210"

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql" / "analysis"
TABLES = ROOT / "results" / "tables"

# logical name -> (sql file, csv glob used for fallback)
SOURCES = {
    "kpi": ("kpi_summary.sql", "kpi_summary_*.csv"),
    "funnel": ("order_funnel.sql", "order_funnel_*.csv"),
    "ttest": ("delay_review_ttest.sql", "delay_review_ttest_*.csv"),
    "delay": ("delay_threshold_analysis.sql", "delay_threshold*.csv"),
    "geo": ("geo_matching_leadtime_analysis.sql", "geo_matching_leadtime_*.csv"),
    "category": (
        "category_delivery_review_by_category.sql",
        "category_delivery_review_by_category_*.csv",
    ),
    "cohort": (
        "cohort_retention_by_delay_experience.sql",
        "cohort_retention_by_delay_*.csv",
    ),
}


def _project_id() -> str:
    try:
        return st.secrets.get("gcp_project_id", DEFAULT_PROJECT_ID)
    except Exception:
        return DEFAULT_PROJECT_ID


@st.cache_resource(show_spinner=False)
def _get_client():
    """BigQuery client.

    Uses a service account from st.secrets when present (for Streamlit
    Community Cloud), otherwise falls back to Application Default Credentials
    (``gcloud auth application-default login``) for local runs.
    """
    from google.cloud import bigquery

    try:
        if "gcp_service_account" in st.secrets:
            from google.oauth2 import service_account

            creds = service_account.Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"])
            )
            return bigquery.Client(credentials=creds, project=_project_id())
    except Exception:
        pass
    return bigquery.Client(project=_project_id())


def _read_sql(filename: str) -> str:
    return (SQL_DIR / filename).read_text()


def _latest_csv(pattern: str) -> Path:
    files = sorted(TABLES.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No CSV matching {pattern} in {TABLES}")
    return files[-1]


@st.cache_data(ttl=3600, show_spinner=False)
def load(name: str) -> dict:
    """Return {'df', 'source', 'detail'} for a logical query name.

    Tries BigQuery first; on any failure, falls back to the committed CSV.
    """
    sql_file, csv_glob = SOURCES[name]
    try:
        client = _get_client()
        df = client.query(_read_sql(sql_file)).to_dataframe()
        return {"df": df, "source": "BigQuery", "detail": sql_file}
    except Exception as exc:  # noqa: BLE001 - fall back to CSV on any error
        csv_path = _latest_csv(csv_glob)
        df = pd.read_csv(csv_path)
        return {
            "df": df,
            "source": "CSV",
            "detail": f"{csv_path.name} ({type(exc).__name__})",
        }


def load_all() -> dict:
    return {name: load(name) for name in SOURCES}


def get_sql(name_or_file: str) -> str:
    """Return the SQL text for a logical query name or a raw filename."""
    filename = SOURCES[name_or_file][0] if name_or_file in SOURCES else name_or_file
    return _read_sql(filename)
