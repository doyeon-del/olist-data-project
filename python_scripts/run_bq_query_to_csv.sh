#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <sql_file_path> <output_basename>"
  echo "Example: $0 sql/analysis/category_delivery_review_analysis.sql category_delivery_review"
  exit 1
fi

SQL_FILE="$1"
OUTPUT_BASENAME="$2"

if [[ ! -f "$SQL_FILE" ]]; then
  echo "Error: SQL file not found: $SQL_FILE"
  exit 1
fi

mkdir -p results/tables

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT_FILE="results/tables/${OUTPUT_BASENAME}_${TIMESTAMP}.csv"

bq query \
  --use_legacy_sql=false \
  --format=csv \
  < "$SQL_FILE" \
  > "$OUTPUT_FILE"

echo "Saved: $OUTPUT_FILE"
