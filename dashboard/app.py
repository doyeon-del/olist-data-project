"""Olist e-commerce delivery & experience dashboard (Streamlit + BigQuery)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import i18n

st.set_page_config(page_title="Olist Delivery & Experience Dashboard", layout="wide")

# Editorial polish on top of the native theme (config.toml): tighter display
# tracking and antialiasing, in the Expo/Inter-style register but set in PretendardGOV.
st.markdown(
    """
    <style>
      html, body, [class*="css"] { -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }
      h1 { font-weight: 600; letter-spacing: -0.03em; font-size: 2.6rem; line-height: 1.08; }
      h2, h3 { font-weight: 600; letter-spacing: -0.02em; }
      [data-testid="stMetricValue"] { font-weight: 600; letter-spacing: -0.02em; }
      [data-testid="stMetricLabel"] p { color: #60646c; font-weight: 500; }
      .stTabs [data-baseweb="tab"] { font-weight: 500; }
      [data-testid="stCaptionContainer"] { color: #60646c; }
    </style>
    """,
    unsafe_allow_html=True,
)

FONT_STACK = "PretendardGOV, -apple-system, system-ui, sans-serif"

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
    font=dict(family=FONT_STACK, color="#171717", size=13),
    title_font=dict(family=FONT_STACK, size=15),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)


# --------------------------------------------------------------------------- #
# Language + data
# --------------------------------------------------------------------------- #
bundle = data.load_all()
all_bigquery = {bundle[k]["source"] for k in bundle} == {"BigQuery"}

with st.sidebar:
    selected = st.segmented_control(
        "언어 / Language", options=list(i18n.LANGS), default="한국어"
    )
    lang = i18n.LANGS.get(selected or "한국어", "ko")
    t = i18n.TEXT[lang]
    vl = i18n.VALUE_LABELS[lang]

    st.subheader(t["sidebar_source"])
    st.write(t["source_live"] if all_bigquery else t["source_fallback"])
    for name in data.SOURCES:
        st.write(f"`{name}` — {bundle[name]['source']}")
    st.divider()
    st.caption(t["sidebar_caption"])

kpi = bundle["kpi"]["df"].iloc[0]
funnel = bundle["funnel"]["df"].iloc[0]
ttest = bundle["ttest"]["df"].set_index("grp")
delay = bundle["delay"]["df"]
geo = bundle["geo"]["df"]
category = bundle["category"]["df"]
cohort = bundle["cohort"]["df"]


# --------------------------------------------------------------------------- #
# Header + KPI cards
# --------------------------------------------------------------------------- #
st.title(t["title"])
st.caption(t["caption"])

c1, c2, c3, c4 = st.columns(4)
c1.metric(t["kpi_orders"], f"{int(kpi['total_orders']):,}", border=True)
c2.metric(t["kpi_leadtime"], f"{kpi['avg_lead_time_days']:.1f} {t['unit_days']}", border=True)
c3.metric(t["kpi_review"], f"{kpi['avg_review_score']:.2f} / 5", border=True)
c4.metric(t["kpi_delay"], f"{kpi['delay_rate_pct']:.1f}%", border=True)
st.divider()


# --------------------------------------------------------------------------- #
# Tabs
# --------------------------------------------------------------------------- #
tabs = st.tabs(
    [
        t["tab_funnel"],
        t["tab_stats"],
        t["tab_delay"],
        t["tab_geo"],
        t["tab_category"],
        t["tab_retention"],
        t["tab_insights"],
    ]
)
tab_funnel, tab_stats, tab_delay, tab_geo, tab_cat, tab_ret, tab_insight = tabs


# ---- Funnel ---------------------------------------------------------------- #
with tab_funnel:
    st.subheader(t["funnel_title"])
    stages = t["funnel_stages"]
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
    st.write(
        t["funnel_text"].format(
            placed=values[0],
            pct=values[3] / values[0] * 100,
            deliver=(values[2] - values[3]) / values[0] * 100,
            ship=(values[1] - values[2]) / values[0] * 100,
        )
    )
    with st.expander(t["funnel_expander"]):
        st.dataframe(
            pd.DataFrame({t["col_stage"]: stages, t["col_orders"]: values}),
            width="stretch",
            hide_index=True,
        )


# ---- Statistical test ------------------------------------------------------ #
with tab_stats:
    st.subheader(t["stats_title"])
    st.info(t["stats_intro"])

    n_d, m_d, s_d = (ttest.loc["delayed", c] for c in ("n", "mean_score", "sd_score"))
    n_o, m_o, s_o = (ttest.loc["on_time", c] for c in ("n", "mean_score", "sd_score"))
    diff = m_o - m_d
    se = math.sqrt(s_o**2 / n_o + s_d**2 / n_d)
    t_stat = diff / se
    df_w = se**4 / ((s_o**2 / n_o) ** 2 / (n_o - 1) + (s_d**2 / n_d) ** 2 / (n_d - 1))
    p_val = 2 * stats.t.sf(abs(t_stat), df_w)
    pooled_sd = math.sqrt(((n_o - 1) * s_o**2 + (n_d - 1) * s_d**2) / (n_o + n_d - 2))
    cohen_d = diff / pooled_sd
    tcrit = stats.t.ppf(0.975, df_w)
    lo, hi = diff - tcrit * se, diff + tcrit * se

    m1, m2, m3 = st.columns(3)
    m1.metric(t["stats_group_ontime"], f"{m_o:.2f}", f"n = {int(n_o):,}", delta_color="off", border=True)
    m2.metric(t["stats_group_delayed"], f"{m_d:.2f}", f"n = {int(n_d):,}", delta_color="off", border=True)
    m3.metric(t["stats_diff"], f"+{diff:.2f}", f"d = {cohen_d:.2f}", delta_color="off", border=True)

    fig = go.Figure(
        go.Bar(
            x=[t["stats_group_ontime"], t["stats_group_delayed"]],
            y=[m_o, m_d],
            error_y=dict(
                type="data",
                array=[1.96 * s_o / math.sqrt(n_o), 1.96 * s_d / math.sqrt(n_d)],
                visible=True,
            ),
            marker_color=[PALETTE["blue"], PALETTE["cross"]],
            text=[f"{m_o:.2f}", f"{m_d:.2f}"],
            textposition="outside",
        )
    )
    fig.update_yaxes(range=[0, 5], title_text=t["stats_axis"])
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(t["stats_metrics_caption"])

    p_str = "< 0.001" if p_val < 0.001 else f"= {p_val:.3f}"
    st.write(
        t["stats_result"].format(diff=diff, lo=lo, hi=hi, df=df_w, t=t_stat, p=p_str, d=cohen_d)
    )
    st.caption(t["stats_caveat"])


# ---- Delivery delay -------------------------------------------------------- #
with tab_delay:
    st.subheader(t["delay_title"])
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(
        x=delay["delay_bucket"],
        y=delay["avg_review_score"],
        marker_color=BUCKET_COLORS[: len(delay)],
        text=[f"{v:.2f}" for v in delay["avg_review_score"]],
        textposition="outside",
        name=t["delay_legend_score"],
    )
    fig.add_scatter(
        x=delay["delay_bucket"],
        y=delay["low_score_rate_pct"],
        mode="lines+markers",
        line=dict(color="#2F2F2F", width=2),
        name=t["delay_legend_low"],
        secondary_y=True,
    )
    fig.update_yaxes(range=[0, 5], title_text=t["delay_y1"], secondary_y=False)
    fig.update_yaxes(range=[0, 100], title_text=t["delay_y2"], secondary_y=True)
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)
    on_time = delay.loc[delay["delay_bucket"].str.startswith("D<=0"), "avg_review_score"].iloc[0]
    st.write(t["delay_text"].format(on_time=on_time, low=delay["low_score_rate_pct"].max()))
    with st.expander(t["delay_expander"]):
        st.dataframe(delay, width="stretch", hide_index=True)


# ---- Geo matching ---------------------------------------------------------- #
with tab_geo:
    st.subheader(t["geo_title"])
    geo_sorted = geo.sort_values("avg_lead_time_days")
    fig = go.Figure()
    fig.add_bar(
        y=[vl[v] for v in geo_sorted["state_match_type"]],
        x=geo_sorted["avg_lead_time_days"],
        orientation="h",
        marker_color=[
            PALETTE["green"] if v == "Same State" else PALETTE["cross"]
            for v in geo_sorted["state_match_type"]
        ],
        text=[f"{v:.2f} {t['unit_days']}" for v in geo_sorted["avg_lead_time_days"]],
        textposition="outside",
    )
    fig.update_layout(xaxis_title=t["geo_axis"], **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(len(geo))
    for col, (_, row) in zip(cols, geo.iterrows()):
        col.metric(
            vl[row["state_match_type"]],
            f"{row['avg_lead_time_days']:.1f} {t['unit_days']}",
            t["geo_delay_rate"].format(v=row["delay_rate_pct"]),
            delta_color="off",
            border=True,
        )
    st.write(t["geo_text"])
    with st.expander(t["geo_expander"]):
        st.dataframe(geo, width="stretch", hide_index=True)


# ---- Category -------------------------------------------------------------- #
with tab_cat:
    st.subheader(t["cat_title"])
    min_orders = st.slider(
        t["cat_slider"],
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
            sizeref=2.0 * cat["total_orders"].max() / (45.0**2),
            sizemin=4,
            color=cat["avg_review_score"],
            colorscale="RdYlGn",
            cmin=3.4,
            cmax=4.6,
            showscale=True,
            colorbar=dict(title=t["cat_hover_review"]),
            line=dict(width=0.5, color="#333"),
        ),
        text=cat["category_name_en"],
        customdata=cat["total_orders"],
        hovertemplate=f"<b>%{{text}}</b><br>{t['cat_hover_lead']}: %{{x:.1f}}<br>"
        f"{t['cat_hover_review']}: %{{y:.2f}}<br>{t['cat_hover_orders']}: %{{customdata:,}}<extra></extra>",
    )
    fig.add_vline(x=avg_lead, line_dash="dash", line_color=PALETTE["gray"])
    fig.add_hline(y=avg_rev, line_dash="dash", line_color=PALETTE["gray"])
    fig.update_layout(xaxis_title=t["cat_x"], yaxis_title=t["cat_y"], **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    st.write(t["cat_weak"])
    weak = cat[(cat["avg_lead_time"] > avg_lead) & (cat["avg_review_score"] < avg_rev)]
    weak = weak.sort_values("avg_review_score").head(8)
    weak = weak[["category_name_en", "total_orders", "avg_lead_time", "avg_review_score"]].rename(
        columns={
            "category_name_en": t["cat_col_name"],
            "total_orders": t["cat_col_orders"],
            "avg_lead_time": t["cat_col_lead"],
            "avg_review_score": t["cat_col_review"],
        }
    )
    st.dataframe(weak, width="stretch", hide_index=True)


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
    st.subheader(t["ret_title"])
    st.info(t["ret_info"])
    curve = build_retention_curve(cohort)
    fig = go.Figure()
    palette = {"Delayed First Order": PALETTE["cross"], "On-time/Early First Order": PALETTE["blue"]}
    for group, g in curve.groupby("first_order_delay_group"):
        fig.add_scatter(
            x=g["cohort_index"],
            y=g["retention_rate"] * 100,
            mode="lines+markers",
            name=vl.get(group, group),
            line=dict(width=2, color=palette.get(group, PALETTE["gray"])),
        )
    fig.update_layout(xaxis_title=t["ret_x"], yaxis_title=t["ret_y"], **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)


# ---- Insights -------------------------------------------------------------- #
with tab_insight:
    st.subheader(t["insights_title"])
    st.markdown(t["insights_body"])
    st.caption(t["insights_caption"])
