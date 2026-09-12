#!/usr/bin/env python3
"""Supplementary checks computed from the raw Kaggle CSVs (no BigQuery needed).

Reproduces three tables that were not part of the original SQL pipeline:
  1. delay_by_day            : review score by exact delay day (-2 .. +8)
  2. geo_state_pair          : lead time / delay rate by seller_state x customer_state
  3. repurchase_by_first_delay: customer-level repurchase rate by first-order delay experience

Raw CSV directory defaults to ~/Downloads; override with OLIST_RAW_DIR.
Definitions mirror sql/analysis/*.sql: delivered orders only, delay_days =
delivered date - estimated date (calendar days), review = mean score per order.
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"
RAW = Path(os.environ.get("OLIST_RAW_DIR", Path.home() / "Downloads"))

TS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def load():
    o = pd.read_csv(RAW / "olist_orders_dataset.csv", parse_dates=TS)
    c = pd.read_csv(RAW / "olist_customers_dataset.csv")
    oi = pd.read_csv(RAW / "olist_order_items_dataset.csv")
    s = pd.read_csv(RAW / "olist_sellers_dataset.csv")
    r = pd.read_csv(RAW / "olist_order_reviews_dataset.csv")

    d = o[o.order_status == "delivered"].dropna(
        subset=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]
    ).copy()
    d["delay_days"] = (
        d.order_delivered_customer_date.dt.normalize() - d.order_estimated_delivery_date.dt.normalize()
    ).dt.days
    d["lead_time_days"] = (
        d.order_delivered_customer_date.dt.normalize() - d.order_purchase_timestamp.dt.normalize()
    ).dt.days
    d = d.merge(c[["customer_id", "customer_unique_id", "customer_state"]], on="customer_id")
    seller_state = oi.merge(s[["seller_id", "seller_state"]], on="seller_id").groupby("order_id").seller_state.first()
    d = d.join(seller_state, on="order_id")
    d = d.join(r.groupby("order_id").review_score.mean().rename("avg_review_score"), on="order_id")
    return d


def delay_by_day(d):
    x = d.dropna(subset=["avg_review_score", "order_approved_at", "order_delivered_carrier_date"])
    x = x[(x.delay_days >= -2) & (x.delay_days <= 8)]
    return (
        x.groupby("delay_days")
        .agg(
            order_count=("avg_review_score", "size"),
            avg_review_score=("avg_review_score", "mean"),
            low_score_rate_pct=("avg_review_score", lambda v: (v <= 2).mean() * 100),
        )
        .round(2)
        .reset_index()
    )


def geo_state_pair(d, min_orders=300):
    x = d.dropna(subset=["seller_state"])
    t = (
        x.groupby(["seller_state", "customer_state"])
        .agg(
            order_count=("lead_time_days", "size"),
            avg_lead_time_days=("lead_time_days", "mean"),
            delay_rate_pct=("delay_days", lambda v: (v > 0).mean() * 100),
            avg_review_score=("avg_review_score", "mean"),
        )
        .round(2)
        .reset_index()
    )
    t["same_state"] = np.where(t.seller_state == t.customer_state, 1, 0)
    return t[t.order_count >= min_orders].sort_values("delay_rate_pct", ascending=False)


def repurchase_by_first_delay(d):
    dd = d.sort_values("order_purchase_timestamp")
    first = dd.groupby("customer_unique_id").first()
    orders = dd.groupby("customer_unique_id").size()
    first["repeat"] = orders > 1
    first["first_order_delay_group"] = np.where(first.delay_days > 0, "Delayed First Order", "On-time/Early First Order")
    t = first.groupby("first_order_delay_group").repeat.agg(customers="size", repeat_customers="sum", repurchase_rate_pct="mean")
    t["repurchase_rate_pct"] = (t.repurchase_rate_pct * 100).round(2)
    return t.reset_index()


if __name__ == "__main__":
    d = load()
    for name, fn in [
        ("delay_by_day", delay_by_day),
        ("geo_state_pair", geo_state_pair),
        ("repurchase_by_first_delay", repurchase_by_first_delay),
    ]:
        df = fn(d)
        path = OUT / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"== {name} -> {path.relative_to(ROOT)}")
        print(df.head(12).to_string(index=False))
