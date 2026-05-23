"""Olist e-commerce delivery & experience dashboard (Streamlit + BigQuery)."""

from __future__ import annotations

import math
import sys
import time
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

# Semantic colors (Airbnb register: ink + a single Rausch voltage, plus a small
# functional set so numbers carry meaning through color, not just weight).
INK = "#222222"
GRAY = "#929292"
ACCENT = "#16a34a"       # primary green (matches config.toml primaryColor)
ACCENT_DK = "#0b6e3b"
ACCENT_LT = "#a9e0bf"
FONT_STACK = "PretendardGOV, -apple-system, system-ui, sans-serif"

# Monochrome green ramp, light -> dark. Single tone family across all charts.
GREENS = ["#dcf3e4", "#a9e0bf", "#76c998", "#46b079", "#1f9254", "#0b6e3b"]
BUCKET_COLORS = GREENS
PLOTLY_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=10, r=10, t=40, b=10),
    font=dict(family=FONT_STACK, color=INK, size=13),
    title=dict(text=""),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)

st.markdown(
    """
    <style>
      html, body, [class*="css"] { -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }
      h1 { font-weight: 700; letter-spacing: -0.02em; font-size: 2rem; line-height: 1.15; }
      h2, h3 { font-weight: 600; letter-spacing: -0.01em; }
      [data-testid="stCaptionContainer"] { color: #6a6a6a; }

      @keyframes riseIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }

      /* number cards */
      .mrow { display: flex; gap: 14px; flex-wrap: wrap; margin: 2px 0 8px; }
      .mcard { flex: 1; min-width: 150px; background: #fff; border: 1px solid #ebebeb;
        border-radius: 14px; padding: 16px 18px;
        box-shadow: rgba(0,0,0,0.02) 0 0 0 1px, rgba(0,0,0,0.04) 0 2px 6px;
        animation: riseIn .5s ease both; }
      .mcard .mlabel { font-size: 13px; color: #6a6a6a; font-weight: 500; margin-bottom: 6px; }
      .mcard .mvalue { font-size: 30px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.05; }
      .mcard .msub { font-size: 12.5px; color: #929292; margin-top: 5px; }

      /* data-source lineage strip */
      .lineage { display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
        margin: 2px 0 14px; }
      .lineage .chip { background: #f7f7f7; border: 1px solid #ebebeb; border-radius: 9999px;
        padding: 5px 13px; font-size: 12.5px; color: #3f3f3f; white-space: nowrap;
        animation: riseIn .5s ease both; }
      .lineage .chip-bq { background: #e7f6ec; border-color: #b6e3c5; color: #0b6e3b; font-weight: 600; }
      .lineage .chip-rows { font-weight: 600; color: #222; }
      .lineage .chip:nth-child(1){animation-delay:.00s;} .lineage .chip:nth-child(3){animation-delay:.06s;}
      .lineage .chip:nth-child(5){animation-delay:.12s;} .lineage .chip:nth-child(7){animation-delay:.18s;}
      .lineage .arrow { color: #c1c1c1; font-size: 13px; }

      /* selected segmented-control button (language toggle + view nav) -> green */
      button[data-testid="stBaseButton-segmented_controlActive"],
      div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
        background-color: #e7f6ec !important;
        color: #0b6e3b !important;
        border-color: #16a34a !important;
      }
      button[data-testid="stBaseButton-segmented_controlActive"] p,
      div[data-testid="stSegmentedControl"] button[aria-pressed="true"] p {
        color: #0b6e3b !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Language + data
# --------------------------------------------------------------------------- #
bundle = data.load_all()
all_bigquery = {bundle[k]["source"] for k in bundle} == {"BigQuery"}

with st.sidebar:
    selected = st.segmented_control(
        "언어 / Language", options=list(i18n.LANGS), default="한국어", key="lang"
    )
    lang = i18n.LANGS.get(selected or "한국어", "ko")
    t = i18n.TEXT[lang]
    vl = i18n.VALUE_LABELS[lang]
    st.divider()
    st.caption(t["sidebar_caption"])

kpi = bundle["kpi"]["df"].iloc[0]
funnel = bundle["funnel"]["df"].iloc[0]
ttest = bundle["ttest"]["df"].set_index("grp")
delay = bundle["delay"]["df"]
geo = bundle["geo"]["df"]
category = bundle["category"]["df"]
cohort = bundle["cohort"]["df"]

# logical view -> (sql file, source tables)
VIEW_META = {
    "funnel": ("order_funnel.sql", ["olist_mart.mart_orders"]),
    "stats": ("delay_review_ttest.sql", ["olist_mart.mart_delivery_features"]),
    "delay": ("delay_threshold_analysis.sql", ["olist_mart.mart_delivery_features"]),
    "geo": ("geo_matching_leadtime_analysis.sql", ["olist_mart.mart_order_items", "olist_mart.mart_orders"]),
    "category": (
        "category_delivery_review_by_category.sql",
        ["olist_mart.mart_order_operational_funnel", "olist_raw.view_products_english", "olist_raw.order_reviews"],
    ),
    "retention": ("cohort_retention_by_delay_experience.sql", ["olist_mart.mart_orders"]),
}
# view name -> data bundle / source key
BUNDLE_OF = {
    "funnel": "funnel",
    "stats": "ttest",
    "delay": "delay",
    "geo": "geo",
    "category": "category",
    "retention": "cohort",
}


def card(label: str, value: str, sub: str, color: str) -> str:
    return (
        f'<div class="mcard"><div class="mlabel">{label}</div>'
        f'<div class="mvalue" style="color:{color}">{value}</div>'
        f'<div class="msub">{sub}</div></div>'
    )


def cards_row(cards: list[str]) -> None:
    st.markdown(f'<div class="mrow">{"".join(cards)}</div>', unsafe_allow_html=True)


def data_lineage(view: str, animate: bool) -> None:
    """Animated source -> query -> result strip + a live query status."""
    sql_file, tables = VIEW_META[view]
    bkey = BUNDLE_OF[view]
    n = len(bundle[bkey]["df"])
    src = bundle[bkey]["source"]
    tbl = tables[0] + (f"  +{len(tables) - 1}" if len(tables) > 1 else "")
    chips = (
        f'<span class="chip chip-bq">{src}</span><span class="arrow">→</span>'
        f'<span class="chip">{tbl}</span><span class="arrow">→</span>'
        f'<span class="chip">{sql_file}</span><span class="arrow">→</span>'
        f'<span class="chip chip-rows">{n} {t["rows"]}</span>'
    )
    st.markdown(f'<div class="lineage">{chips}</div>', unsafe_allow_html=True)
    with st.status(t["query_running"], expanded=False) as s:
        data.load(bkey)
        if animate:
            time.sleep(0.3)  # only on an actual view switch, so the live-query movement shows
        st.code(data.get_sql(sql_file), language="sql")
        s.update(label=t["query_done"].format(n=n), state="complete")


# --------------------------------------------------------------------------- #
# Header + KPI number cards
# --------------------------------------------------------------------------- #
st.title(t["title"])
st.caption(t["caption"])

cards_row(
    [
        card(t["kpi_orders"], f"{int(kpi['total_orders']):,}", "delivered", INK),
        card(t["kpi_leadtime"], f"{kpi['avg_lead_time_days']:.1f}", t["unit_days"], INK),
        card(t["kpi_review"], f"{kpi['avg_review_score']:.2f}", "/ 5", INK),
        card(t["kpi_delay"], f"{kpi['delay_rate_pct']:.1f}%", "", INK),
    ]
)
st.divider()


# --------------------------------------------------------------------------- #
# View navigation (rerun on change -> lineage + query animate every switch)
# --------------------------------------------------------------------------- #
VIEWS = ["funnel", "stats", "delay", "geo", "category", "retention", "insights"]
if "view" not in st.session_state:
    _qp_view = st.query_params.get("view")
    st.session_state["view"] = _qp_view if _qp_view in VIEWS else "funnel"
view = st.segmented_control(
    t["nav_label"],
    VIEWS,
    format_func=lambda k: t[f"tab_{k}"],
    key="view",
    label_visibility="collapsed",
)
view = view or st.session_state["view"]
view_changed = st.session_state.get("_prev_view") != view
st.session_state["_prev_view"] = view
st.write("")

if view != "insights":
    data_lineage(view, animate=view_changed)


# ---- Funnel ---------------------------------------------------------------- #
if view == "funnel":
    st.subheader(t["funnel_title"])
    stages = t["funnel_stages"]
    values = [int(funnel[c]) for c in ("purchased", "approved", "shipped", "delivered")]
    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker_color=[GREENS[1], GREENS[2], GREENS[3], GREENS[5]],
            connector=dict(line=dict(color=GRAY, width=1)),
        )
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)
    ship = (values[1] - values[2]) / values[0] * 100
    deliver = (values[2] - values[3]) / values[0] * 100
    bottleneck = t["funnel_leg_approve"] if ship >= deliver else t["funnel_leg_deliver"]
    st.write(
        t["funnel_text"].format(
            placed=values[0], pct=values[3] / values[0] * 100, ship=ship, deliver=deliver,
            bottleneck=bottleneck,
        )
    )
    with st.expander(t["funnel_expander"]):
        st.dataframe(
            pd.DataFrame({"stage": stages, "orders": values}),
            width="stretch",
            hide_index=True,
            column_config={
                "stage": st.column_config.TextColumn(t["c_stage"]),
                "orders": st.column_config.NumberColumn(t["c_orders"], format="%d"),
            },
        )


# ---- Statistical test ------------------------------------------------------ #
elif view == "stats":
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

    cards_row(
        [
            card(t["stats_group_ontime"], f"{m_o:.2f}", f"n = {int(n_o):,}", INK),
            card(t["stats_group_delayed"], f"{m_d:.2f}", f"n = {int(n_d):,}", INK),
            card(t["stats_diff"], f"+{diff:.2f}", f"Cohen's d = {cohen_d:.2f}", ACCENT),
        ]
    )

    fig = go.Figure(
        go.Bar(
            x=[t["stats_group_ontime"], t["stats_group_delayed"]],
            y=[m_o, m_d],
            error_y=dict(
                type="data",
                array=[1.96 * s_o / math.sqrt(n_o), 1.96 * s_d / math.sqrt(n_d)],
                visible=True,
            ),
            marker_color=[ACCENT_DK, ACCENT_LT],
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
elif view == "delay":
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
        line=dict(color=INK, width=2),
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
        st.dataframe(
            delay,
            width="stretch",
            hide_index=True,
            column_config={
                "delay_bucket": st.column_config.TextColumn(t["c_bucket"]),
                "order_count": st.column_config.NumberColumn(t["c_orders"], format="%d"),
                "avg_delay_days": st.column_config.NumberColumn(t["c_avg_delay"], format="%.1f"),
                "avg_review_score": st.column_config.ProgressColumn(
                    t["c_avg_review"], format="%.2f", min_value=0, max_value=5
                ),
                "low_score_rate_pct": st.column_config.NumberColumn(t["c_low_rate"], format="%.1f%%"),
            },
        )


# ---- Geo matching ---------------------------------------------------------- #
elif view == "geo":
    st.subheader(t["geo_title"])
    cards_row(
        [
            card(
                vl[row["state_match_type"]],
                f"{row['avg_lead_time_days']:.1f} {t['unit_days']}",
                t["geo_delay_rate"].format(v=row["delay_rate_pct"]),
                ACCENT if row["state_match_type"] == "Same State" else INK,
            )
            for _, row in geo.iterrows()
        ]
    )
    geo_sorted = geo.sort_values("avg_lead_time_days")
    fig = go.Figure()
    fig.add_bar(
        y=[vl[v] for v in geo_sorted["state_match_type"]],
        x=geo_sorted["avg_lead_time_days"],
        orientation="h",
        marker_color=[ACCENT_DK if v == "Same State" else ACCENT_LT for v in geo_sorted["state_match_type"]],
        text=[f"{v:.2f} {t['unit_days']}" for v in geo_sorted["avg_lead_time_days"]],
        textposition="outside",
    )
    fig.update_layout(xaxis_title=t["geo_axis"], **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)
    st.write(t["geo_text"])
    with st.expander(t["geo_expander"]):
        geo_disp = geo.copy()
        geo_disp["state_match_type"] = geo_disp["state_match_type"].map(vl)
        st.dataframe(
            geo_disp,
            width="stretch",
            hide_index=True,
            column_config={
                "state_match_type": st.column_config.TextColumn(t["c_match"]),
                "order_count": st.column_config.NumberColumn(t["c_orders"], format="%d"),
                "avg_lead_time_days": st.column_config.NumberColumn(t["c_avg_leadtime"], format="%.1f"),
                "avg_delay_days": st.column_config.NumberColumn(t["c_avg_delay"], format="%.1f"),
                "avg_review_score": st.column_config.ProgressColumn(
                    t["c_avg_review"], format="%.2f", min_value=0, max_value=5
                ),
                "delay_rate_pct": st.column_config.NumberColumn(t["c_delay_rate"], format="%.2f%%"),
            },
        )


# ---- Category -------------------------------------------------------------- #
elif view == "category":
    st.subheader(t["cat_title"])
    st.caption(t["cat_desc"])
    min_orders = st.slider(
        t["cat_slider"],
        int(category["total_orders"].min()),
        int(category["total_orders"].max()),
        int(max(category["total_orders"].min(), 100)),
        step=50,
        help=t["cat_slider_help"],
    )
    cat = category[category["total_orders"] >= min_orders].copy()
    st.caption(t["cat_shown"].format(n=len(cat)))
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
            colorscale="Greens",
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
    fig.add_vline(x=avg_lead, line_dash="dash", line_color=GRAY)
    fig.add_hline(y=avg_rev, line_dash="dash", line_color=GRAY)
    fig.update_layout(xaxis_title=t["cat_x"], yaxis_title=t["cat_y"], **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    st.write(t["cat_weak"])
    weak = cat[(cat["avg_lead_time"] > avg_lead) & (cat["avg_review_score"] < avg_rev)]
    weak = weak.sort_values("avg_review_score").head(8)
    st.dataframe(
        weak[["category_name_en", "total_orders", "avg_lead_time", "avg_review_score"]],
        width="stretch",
        hide_index=True,
        column_config={
            "category_name_en": st.column_config.TextColumn(t["cat_col_name"]),
            "total_orders": st.column_config.NumberColumn(t["c_orders"], format="%d"),
            "avg_lead_time": st.column_config.NumberColumn(t["c_avg_leadtime"], format="%.1f"),
            "avg_review_score": st.column_config.ProgressColumn(
                t["c_avg_review"], format="%.2f", min_value=0, max_value=5
            ),
        },
    )


# ---- Retention ------------------------------------------------------------- #
elif view == "retention":

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

    st.subheader(t["ret_title"])
    st.info(t["ret_info"])
    curve = build_retention_curve(cohort)
    fig = go.Figure()
    palette = {"Delayed First Order": ACCENT_LT, "On-time/Early First Order": ACCENT_DK}
    for group, g in curve.groupby("first_order_delay_group"):
        fig.add_scatter(
            x=g["cohort_index"],
            y=g["retention_rate"] * 100,
            mode="lines+markers",
            name=vl.get(group, group),
            line=dict(width=2, color=palette.get(group, GRAY)),
        )
    fig.update_layout(xaxis_title=t["ret_x"], yaxis_title=t["ret_y"], **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)


# ---- Insights -------------------------------------------------------------- #
elif view == "insights":
    st.subheader(t["insights_title"])

    def _go(target: str) -> None:
        st.session_state["view"] = target

    ontime = delay.loc[delay["delay_bucket"].str.startswith("D<=0"), "avg_review_score"].iloc[0]
    late = delay.loc[delay["delay_bucket"] == "D+3~4", "avg_review_score"].iloc[0]
    same = geo.loc[geo["state_match_type"] == "Same State", "avg_lead_time_days"].iloc[0]
    cross = geo.loc[geo["state_match_type"] == "Cross State", "avg_lead_time_days"].iloc[0]
    worst = category.sort_values("avg_lead_time", ascending=False).iloc[0]

    insights = [
        ("delay", t["insight_1_title"], t["insight_1_body"].format(ontime=ontime, late=late)),
        ("geo", t["insight_2_title"], t["insight_2_body"].format(same=same, cross=cross)),
        (
            "category",
            t["insight_3_title"],
            t["insight_3_body"].format(
                cat=worst["category_name_en"], lead=worst["avg_lead_time"], rev=worst["avg_review_score"]
            ),
        ),
        ("retention", t["insight_4_title"], t["insight_4_body"]),
    ]
    for target, title, body in insights:
        with st.container(border=True):
            st.markdown(f"#### {title}")
            st.markdown(body)
            st.button(
                t["insight_goto"].format(tab=t[f"tab_{target}"]),
                key=f"goto_{target}",
                on_click=_go,
                args=(target,),
            )
    st.caption(t["insights_caption"])
