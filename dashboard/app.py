"""Olist e-commerce delivery & experience dashboard (Streamlit + BigQuery)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data

st.set_page_config(
    page_title="Olist Delivery & Experience Dashboard",
    page_icon="📦",
    layout="wide",
)

PALETTE = {
    "blue": "#4C78A8",
    "teal": "#72B7B2",
    "yellow": "#F2CF5B",
    "orange": "#F58518",
    "red": "#E45756",
    "purple": "#B279A2",
    "green": "#59A14F",
    "cross": "#E15759",
    "gray": "#8C8C8C",
}
BUCKET_COLORS = [PALETTE[c] for c in ("blue", "teal", "yellow", "orange", "red", "purple")]

PLOTLY_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=10, r=10, t=50, b=10),
    title_font=dict(size=16),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)


# --------------------------------------------------------------------------- #
# Load data
# --------------------------------------------------------------------------- #
bundle = data.load_all()
kpi = bundle["kpi"]["df"].iloc[0]
delay = bundle["delay"]["df"]
geo = bundle["geo"]["df"]
category = bundle["category"]["df"]
cohort = bundle["cohort"]["df"]

sources = {bundle[k]["source"] for k in bundle}
primary_source = "BigQuery" if sources == {"BigQuery"} else "Mixed / CSV fallback"


# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
st.title("📦 Olist Delivery & Experience Dashboard")
st.caption(
    "How delivery performance shapes customer satisfaction in a Brazilian "
    "marketplace — built on the Olist public dataset (BigQuery → Streamlit)."
)

with st.sidebar:
    st.header("Data source")
    if primary_source == "BigQuery":
        st.success("Live from BigQuery")
    else:
        st.warning("CSV fallback (BigQuery unavailable)")
    for name in data.SOURCES:
        b = bundle[name]
        icon = "🟢" if b["source"] == "BigQuery" else "🟡"
        st.write(f"{icon} **{name}** — {b['detail']}")
    st.divider()
    st.caption(
        "Project: `olist-analysis-project-495210`\n\n"
        "Queries read from `sql/analysis/*.sql`."
    )


# --------------------------------------------------------------------------- #
# KPI cards
# --------------------------------------------------------------------------- #
c1, c2, c3, c4 = st.columns(4)
c1.metric("Delivered orders", f"{int(kpi['total_orders']):,}")
c2.metric("Avg lead time", f"{kpi['avg_lead_time_days']:.1f} days")
c3.metric("Avg review score", f"{kpi['avg_review_score']:.2f} / 5")
c4.metric("Delay rate", f"{kpi['delay_rate_pct']:.1f}%")

st.divider()


# --------------------------------------------------------------------------- #
# Tabs
# --------------------------------------------------------------------------- #
tab_delay, tab_geo, tab_cat, tab_ret, tab_insight = st.tabs(
    ["🚚 Delivery delay", "🗺️ Geo matching", "🏷️ Category", "🔁 Retention", "💡 Insights"]
)


# ---- Delivery delay -------------------------------------------------------- #
with tab_delay:
    st.subheader("Review score drops sharply once orders run late")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(
        x=delay["delay_bucket"],
        y=delay["avg_review_score"],
        marker_color=BUCKET_COLORS[: len(delay)],
        text=[f"{v:.2f}" for v in delay["avg_review_score"]],
        textposition="outside",
        name="Avg review score",
    )
    fig.add_scatter(
        x=delay["delay_bucket"],
        y=delay["low_score_rate_pct"],
        mode="lines+markers",
        line=dict(color="#2F2F2F", width=2.5),
        name="Low-score rate (%)",
        secondary_y=True,
    )
    fig.update_yaxes(range=[0, 5], title_text="Avg review score", secondary_y=False)
    fig.update_yaxes(range=[0, 100], title_text="Low-score rate (%)", secondary_y=True)
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        "- On-time/early orders average **{:.2f}**, but reviews fall to **{:.2f}** "
        "at 3–4 days late.\n- The share of low scores (≤2) climbs past **{:.0f}%** "
        "for delays of a week or more.".format(
            delay.loc[delay["delay_bucket"].str.startswith("D<=0"), "avg_review_score"].iloc[0],
            delay.loc[delay["delay_bucket"] == "D+3~4", "avg_review_score"].iloc[0]
            if (delay["delay_bucket"] == "D+3~4").any()
            else delay["avg_review_score"].iloc[2],
            delay["low_score_rate_pct"].max(),
        )
    )
    with st.expander("View data"):
        st.dataframe(delay, width="stretch", hide_index=True)


# ---- Geo matching ---------------------------------------------------------- #
with tab_geo:
    st.subheader("Cross-state orders take about twice as long")
    geo_sorted = geo.sort_values("avg_lead_time_days")
    fig = go.Figure()
    fig.add_bar(
        y=geo_sorted["state_match_type"],
        x=geo_sorted["avg_lead_time_days"],
        orientation="h",
        marker_color=[
            PALETTE["green"] if v == "Same State" else PALETTE["cross"]
            for v in geo_sorted["state_match_type"]
        ],
        text=[f"{v:.2f} days" for v in geo_sorted["avg_lead_time_days"]],
        textposition="outside",
    )
    fig.update_layout(xaxis_title="Average lead time (days)", **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(len(geo))
    for col, (_, row) in zip(cols, geo.iterrows()):
        col.metric(
            row["state_match_type"],
            f"{row['avg_lead_time_days']:.1f} days",
            f"delay rate {row['delay_rate_pct']:.2f}%",
            delta_color="off",
        )
    st.markdown(
        "Seller–customer co-location is one of the strongest levers on lead time. "
        "Same-state orders also see a lower delay rate."
    )
    with st.expander("View data"):
        st.dataframe(geo, width="stretch", hide_index=True)


# ---- Category -------------------------------------------------------------- #
with tab_cat:
    st.subheader("Longer lead times tend to coincide with weaker reviews")
    min_orders = st.slider(
        "Minimum orders per category",
        int(category["total_orders"].min()),
        int(category["total_orders"].max()),
        int(max(category["total_orders"].min(), 100)),
        step=50,
    )
    cat = category[category["total_orders"] >= min_orders].copy()

    avg_lead = cat["avg_lead_time"].mean()
    avg_rev = cat["avg_review_score"].mean()
    fig = go.Figure()
    fig.add_scatter(
        x=cat["avg_lead_time"],
        y=cat["avg_review_score"],
        mode="markers",
        marker=dict(
            size=cat["total_orders"],
            sizemode="area",
            sizeref=2.0 * cat["total_orders"].max() / (45.0 ** 2),
            sizemin=4,
            color=cat["avg_review_score"],
            colorscale="RdYlGn",
            cmin=3.4,
            cmax=4.6,
            showscale=True,
            colorbar=dict(title="Review"),
            line=dict(width=0.5, color="#333"),
        ),
        text=cat["category_name_en"],
        hovertemplate="<b>%{text}</b><br>Lead time: %{x:.1f}d<br>"
        "Review: %{y:.2f}<br>Orders: %{marker.size:,}<extra></extra>",
    )
    fig.add_vline(x=avg_lead, line_dash="dash", line_color=PALETTE["gray"])
    fig.add_hline(y=avg_rev, line_dash="dash", line_color=PALETTE["gray"])
    fig.update_layout(
        xaxis_title="Average lead time (days)",
        yaxis_title="Average review score",
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Weakest categories** (long lead time, low review):")
    weak = cat[(cat["avg_lead_time"] > avg_lead) & (cat["avg_review_score"] < avg_rev)]
    weak = weak.sort_values("avg_review_score").head(8)
    st.dataframe(
        weak[["category_name_en", "total_orders", "avg_lead_time", "avg_review_score"]],
        width="stretch",
        hide_index=True,
    )


# ---- Retention ------------------------------------------------------------- #
def build_retention_curve(df: pd.DataFrame, max_index: int = 12) -> pd.DataFrame:
    df = df.copy()
    df["cohort_month"] = pd.to_datetime(df["cohort_month"])
    cohorts = df[["cohort_month", "first_order_delay_group", "cohort_size"]].drop_duplicates()
    rows = []
    for _, r in cohorts.iterrows():
        for idx in range(max_index + 1):
            rows.append(
                {
                    "cohort_month": r["cohort_month"],
                    "first_order_delay_group": r["first_order_delay_group"],
                    "cohort_size": r["cohort_size"],
                    "cohort_index": idx,
                }
            )
    grid = pd.DataFrame(rows)
    observed = df[["cohort_month", "first_order_delay_group", "cohort_index", "retained_customers"]]
    merged = grid.merge(
        observed, on=["cohort_month", "first_order_delay_group", "cohort_index"], how="left"
    )
    merged["retained_customers"] = merged["retained_customers"].fillna(0)
    summary = merged.groupby(
        ["first_order_delay_group", "cohort_index"], as_index=False
    ).agg({"retained_customers": "sum", "cohort_size": "sum"})
    summary["retention_rate"] = summary["retained_customers"] / summary["cohort_size"]
    return summary[(summary["cohort_index"] >= 1) & (summary["cohort_index"] <= max_index)]


with tab_ret:
    st.subheader("Repeat purchase is rare — retention stays below 1%")
    st.info(
        "⚠️ Olist is a near one-time-purchase marketplace: post-first-month "
        "retention is under 1% for every cohort, and the 'delayed first order' "
        "group is very small. Read the gap below as directional, not conclusive.",
        icon="⚠️",
    )
    curve = build_retention_curve(cohort)
    fig = go.Figure()
    palette = {
        "Delayed First Order": PALETTE["cross"],
        "On-time/Early First Order": PALETTE["blue"],
    }
    for group, g in curve.groupby("first_order_delay_group"):
        fig.add_scatter(
            x=g["cohort_index"],
            y=g["retention_rate"] * 100,
            mode="lines+markers",
            name=group,
            line=dict(width=2.5, color=palette.get(group, PALETTE["gray"])),
        )
    fig.update_layout(
        xaxis_title="Months since first purchase",
        yaxis_title="Retention rate (%)",
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---- Insights -------------------------------------------------------------- #
with tab_insight:
    st.subheader("Key insights & recommendations")
    st.markdown(
        """
**1. Delivery delay is the dominant satisfaction driver.**
Reviews collapse from ~4.3 (on time) to ~2.6 once an order is 3–4 days late, and
most ratings turn negative beyond a week. *Recommendation:* treat "days late vs.
estimate" as the primary CX guardrail and trigger proactive comms once an order
crosses the 2-day threshold.

**2. Geography sets the speed ceiling.**
Cross-state orders take ~2× longer (≈14.7 vs ≈7.5 days). *Recommendation:* prioritise
seller distribution / regional fulfilment for high-volume states to compress lead time.

**3. A few categories carry outsized delivery risk.**
`office_furniture` and other bulky categories pair the longest lead times with the
lowest reviews. *Recommendation:* set category-specific delivery estimates and SLAs
rather than a single marketplace-wide promise.

**4. This is a one-time-purchase marketplace.**
Retention is <1% regardless of first-order experience, so growth depends on
acquisition and first-order quality, not repeat behaviour. *Recommendation:* make the
first delivery count — it is effectively the whole relationship.
"""
    )
    st.caption(
        "Analysis: SQL marts on BigQuery → aggregated queries in `sql/analysis/` → "
        "this dashboard. See README for the full pipeline."
    )
