#!/usr/bin/env python3
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "results/.matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"


def save_fig(path):
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def plot_delay_threshold():
    df = pd.read_csv(TABLES / "delay_threshold.csv")

    fig, ax1 = plt.subplots(figsize=(9, 5))
    x = range(len(df))

    bars = ax1.bar(
        x,
        df["avg_review_score"],
        color=["#4C78A8", "#72B7B2", "#F2CF5B", "#F58518", "#E45756", "#B279A2"],
        width=0.62,
    )
    ax1.set_ylim(0, 5)
    ax1.set_ylabel("Average review score")
    ax1.set_xticks(x)
    ax1.set_xticklabels(df["delay_bucket"], rotation=20, ha="right")
    ax1.set_title("Review score drops sharply after 3+ days of delay", loc="left", fontsize=14, weight="bold")

    for bar, score in zip(bars, df["avg_review_score"]):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.08,
            f"{score:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax2 = ax1.twinx()
    ax2.plot(x, df["low_score_rate_pct"], color="#2F2F2F", marker="o", linewidth=2.2)
    ax2.set_ylabel("Low-score rate (%)")
    ax2.set_ylim(0, 100)

    ax1.grid(axis="y", alpha=0.18)
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    fig.text(
        0.01,
        0.01,
        "Source: results/tables/delay_threshold.csv",
        fontsize=8,
        color="#666666",
    )
    save_fig(FIGURES / "delay_threshold_review_score.png")


def plot_geo_matching():
    df = pd.read_csv(TABLES / "geo_matching_leadtime_20260515_164439.csv")
    df = df.sort_values("avg_lead_time_days", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    y = range(len(df))
    colors = ["#59A14F" if v == "Same State" else "#E15759" for v in df["state_match_type"]]

    bars = ax.barh(y, df["avg_lead_time_days"], color=colors, height=0.48)
    ax.set_yticks(y)
    ax.set_yticklabels(df["state_match_type"])
    ax.set_xlabel("Average lead time (days)")
    ax.set_title("Cross-state orders take about twice as long to deliver", loc="left", fontsize=14, weight="bold")
    ax.grid(axis="x", alpha=0.18)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar, lead, delay_rate in zip(bars, df["avg_lead_time_days"], df["delay_rate_pct"]):
        ax.text(
            lead + 0.25,
            bar.get_y() + bar.get_height() / 2,
            f"{lead:.2f} days | delay rate {delay_rate:.2f}%",
            va="center",
            fontsize=9,
        )

    fig.text(
        0.01,
        0.01,
        "Source: results/tables/geo_matching_leadtime_20260515_164439.csv",
        fontsize=8,
        color="#666666",
    )
    save_fig(FIGURES / "geo_matching_leadtime.png")


def plot_cohort_retention():
    df = pd.read_csv(TABLES / "cohort_retention_by_delay_20260515_164431.csv", parse_dates=["cohort_month"])
    max_index = 12

    cohorts = df[["cohort_month", "first_order_delay_group", "cohort_size"]].drop_duplicates()
    grid_rows = []
    for _, row in cohorts.iterrows():
        for idx in range(max_index + 1):
            grid_rows.append(
                {
                    "cohort_month": row["cohort_month"],
                    "first_order_delay_group": row["first_order_delay_group"],
                    "cohort_size": row["cohort_size"],
                    "cohort_index": idx,
                }
            )

    grid = pd.DataFrame(grid_rows)
    observed = df[["cohort_month", "first_order_delay_group", "cohort_index", "retained_customers"]]
    merged = grid.merge(
        observed,
        on=["cohort_month", "first_order_delay_group", "cohort_index"],
        how="left",
    )
    merged["retained_customers"] = merged["retained_customers"].fillna(0)

    summary = (
        merged.groupby(["first_order_delay_group", "cohort_index"], as_index=False)
        .agg({"retained_customers": "sum", "cohort_size": "sum"})
    )
    summary["retention_rate"] = summary["retained_customers"] / summary["cohort_size"]
    summary = summary[(summary["cohort_index"] >= 1) & (summary["cohort_index"] <= max_index)]

    fig, ax = plt.subplots(figsize=(9, 5))
    palette = {
        "Delayed First Order": "#E15759",
        "On-time/Early First Order": "#4C78A8",
    }
    for group, group_df in summary.groupby("first_order_delay_group"):
        ax.plot(
            group_df["cohort_index"],
            group_df["retention_rate"] * 100,
            marker="o",
            linewidth=2.2,
            color=palette.get(group, "#666666"),
            label=group,
        )

    ax.set_title("Post-first-month retention stays below 1%", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Months since first purchase")
    ax.set_ylabel("Retention rate (%)")
    ax.set_xticks(range(1, max_index + 1))
    ax.set_ylim(0, 0.8)
    ax.grid(axis="y", alpha=0.18)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="upper right")
    fig.text(
        0.01,
        0.01,
        "Source: results/tables/cohort_retention_by_delay_20260515_164431.csv",
        fontsize=8,
        color="#666666",
    )
    save_fig(FIGURES / "cohort_retention_by_delay.png")


def plot_category_delivery_review():
    csv_files = sorted(TABLES.glob("category_delivery_review_by_category_*.csv"))
    if not csv_files:
        raise FileNotFoundError("No category_delivery_review_by_category_*.csv file found")

    latest_csv = csv_files[-1]
    df = pd.read_csv(latest_csv)
    avg_lead_time = df["avg_lead_time"].mean()
    avg_review_score = df["avg_review_score"].mean()

    fig, ax = plt.subplots(figsize=(9, 5.6))
    sizes = (df["total_orders"] / df["total_orders"].max()) * 850 + 50

    scatter = ax.scatter(
        df["avg_lead_time"],
        df["avg_review_score"],
        s=sizes,
        c=df["avg_review_score"],
        cmap="RdYlGn",
        vmin=3.4,
        vmax=4.6,
        alpha=0.82,
        edgecolor="#333333",
        linewidth=0.4,
    )

    ax.axvline(avg_lead_time, color="#666666", linestyle="--", linewidth=1, alpha=0.65)
    ax.axhline(avg_review_score, color="#666666", linestyle="--", linewidth=1, alpha=0.65)
    ax.text(
        avg_lead_time + 0.1,
        ax.get_ylim()[0] + 0.03,
        "Avg lead time",
        fontsize=8,
        color="#555555",
    )
    ax.text(
        ax.get_xlim()[0] + 0.1,
        avg_review_score + 0.02,
        "Avg review",
        fontsize=8,
        color="#555555",
    )

    label_offsets = {
        "office_furniture": (-118, 8),
        "bed_bath_table": (12, 8),
        "computers_accessories": (12, -22),
        "books_general_interest": (14, 8),
        "fashion_male_clothing": (12, -14),
        "fixed_telephony": (12, 10),
    }
    for _, row in df[df["category_name_en"].isin(label_offsets.keys())].iterrows():
        ax.annotate(
            row["category_name_en"],
            (row["avg_lead_time"], row["avg_review_score"]),
            xytext=label_offsets[row["category_name_en"]],
            textcoords="offset points",
            fontsize=8,
            color="#222222",
        )

    ax.set_title("Longer lead times often coincide with weaker review scores", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Average lead time (days)")
    ax.set_ylabel("Average review score")
    ax.set_xlim(df["avg_lead_time"].min() - 0.55, df["avg_lead_time"].max() + 0.9)
    ax.set_ylim(3.35, 4.6)
    ax.grid(alpha=0.18)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    colorbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    colorbar.set_label("Average review score")
    fig.text(
        0.01,
        0.01,
        f"Source: {latest_csv.relative_to(ROOT)} | Bubble size: order count",
        fontsize=8,
        color="#666666",
    )
    save_fig(FIGURES / "category_delivery_review_bubble.png")


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / ".matplotlib").mkdir(parents=True, exist_ok=True)
    plot_delay_threshold()
    plot_geo_matching()
    plot_cohort_retention()
    plot_category_delivery_review()
    print("Saved figures:")
    for path in sorted(FIGURES.glob("*.png")):
        print(f"- {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
