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
    margin=dict(l=10, r=10, t=40, b=10),
    title_font=dict(size=15),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)


# --------------------------------------------------------------------------- #
# Load data
# --------------------------------------------------------------------------- #
bundle = data.load_all()
kpi = bundle["kpi"]["df"].iloc[0]
funnel = bundle["funnel"]["df"].iloc[0]
delay = bundle["delay"]["df"]
geo = bundle["geo"]["df"]
category = bundle["category"]["df"]
cohort = bundle["cohort"]["df"]

all_bigquery = {bundle[k]["source"] for k in bundle} == {"BigQuery"}


# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
st.title("Olist Delivery & Experience")
st.caption(
    "Where delivery performance affects customer ratings in the Olist Brazilian "
    "marketplace dataset. Source: BigQuery, queried live by this app."
)

with st.sidebar:
    st.subheader("Data source")
    st.write("Live from BigQuery" if all_bigquery else "CSV fallback (BigQuery unavailable)")
    for name in data.SOURCES:
        b = bundle[name]
        st.write(f"`{name}` — {b['source']}")
    st.divider()
    st.caption(
        "Project `olist-analysis-project-495210`. "
        "Each tab runs the matching query in `sql/analysis/`."
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
tab_funnel, tab_delay, tab_geo, tab_cat, tab_ret, tab_insight = st.tabs(
    ["Funnel", "Delivery delay", "Geo matching", "Category", "Retention", "Insights"]
)


# ---- Funnel ---------------------------------------------------------------- #
with tab_funnel:
    st.subheader("Order fulfillment funnel")
    stages = ["Purchased", "Approved", "Shipped to carrier", "Delivered"]
    values = [int(funnel[c]) for c in ("purchased", "approved", "shipped", "delivered")]
    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker_color=[PALETTE["blue"], PALETTE["teal"], PALETTE["yellow"], PALETTE["green"]],
            connector=dict(line=dict(color=PALETTE["gray"], width=1)),
        )
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    drop_ship = (values[1] - values[2]) / values[0] * 100
    drop_deliver = (values[2] - values[3]) / values[0] * 100
    st.write(
        f"Of {values[0]:,} placed orders, {values[3] / values[0] * 100:.1f}% reach the "
        f"customer. The largest leak is the carrier-to-customer leg "
        f"({drop_deliver:.1f}% of orders), ahead of approval-to-carrier ({drop_ship:.1f}%)."
    )
    with st.expander("Stage counts"):
        st.dataframe(
            pd.DataFrame({"stage": stages, "orders": values}),
            width="stretch",
            hide_index=True,
        )


# ---- Delivery delay -------------------------------------------------------- #
with tab_delay:
    st.subheader("Review score by days late vs. estimate")
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
        line=dict(color="#2F2F2F", width=2),
        name="Low-score rate (%)",
        secondary_y=True,
    )
    fig.update_yaxes(range=[0, 5], title_text="Avg review score", secondary_y=False)
    fig.update_yaxes(range=[0, 100], title_text="Low-score rate (%)", secondary_y=True)
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)
    on_time = delay.loc[delay["delay_bucket"].str.startswith("D<=0"), "avg_review_score"].iloc[0]
    st.write(
        f"On-time and early orders average {on_time:.2f}. Ratings fall through the "
        f"3-4 day bucket and the share of low scores (2 or below) rises past "
        f"{delay['low_score_rate_pct'].max():.0f}% once orders run a week or more late."
    )
    with st.expander("Query result"):
        st.dataframe(delay, width="stretch", hide_index=True)


# ---- Geo matching ---------------------------------------------------------- #
with tab_geo:
    st.subheader("Lead time by seller-customer location")
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
    st.write(
        "Orders shipped within the customer's own state arrive in about half the time "
        "and miss the estimate less often."
    )
    with st.expander("Query result"):
        st.dataframe(geo, width="stretch", hide_index=True)


# ---- Category -------------------------------------------------------------- #
with tab_cat:
    st.subheader("Lead time vs. review score by category")
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

    st.write("Categories below the average review and above the average lead time:")
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
    st.subheader("Retention by first-order delivery experience")
    st.info(
        "Olist is close to a one-time-purchase marketplace: post-first-month retention "
        "stays under 1% for every cohort, and the delayed-first-order group is small. "
        "Read the gap below as directional, not conclusive.",
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
            line=dict(width=2, color=palette.get(group, PALETTE["gray"])),
        )
    fig.update_layout(
        xaxis_title="Months since first purchase",
        yaxis_title="Retention rate (%)",
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---- Insights -------------------------------------------------------------- #
with tab_insight:
    st.subheader("What the data says")
    st.markdown(
        """
**Lateness matters more than raw speed.**
Average review falls from 4.28 on on-time orders to 2.58 once an order is 3-4 days
past its estimate, and below 2.0 beyond a week. The signal is "later than promised,"
not the absolute number of days in transit.

**Distance sets the speed ceiling.**
Same-state orders arrive in about 7.5 days against 14.7 for cross-state. Seller mix by
region is therefore a structural lever on lead time, not just a logistics detail.

**Delivery risk is concentrated in a few bulky categories.**
office_furniture and similar categories combine the longest lead times with the lowest
reviews, so one marketplace-wide delivery estimate under-serves them.

**Repeat purchase is close to absent.**
Retention sits below 1% across cohorts, so the first order is effectively the whole
relationship. The same scarcity is why the delay-vs-retention comparison can only be
read as directional.
"""
    )
    st.caption("Pipeline: BigQuery marts to aggregated queries in `sql/analysis/` to this app.")
