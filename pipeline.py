"""Multi-center reporting pipeline.

Normalizes inconsistent monthly data from three regional centers into a
single schema, then generates a standardized Excel report with two
summary sheets.
"""

from pathlib import Path
import pandas as pd
import duckdb

DATA = Path(__file__).resolve().parent / "data"

# Load the three regional files
east  = pd.read_csv(DATA / "east.csv")
west  = pd.read_csv(DATA / "west.csv")
north = pd.read_csv(DATA / "north.csv")

# East: estimate missing participants using the average completion ratio
east["cpratio"] = east["completed"] / east["participants"]
cpave = east["cpratio"].mean()
missing = east["participants"].isna()
east.loc[missing, "participants"] = (east.loc[missing, "completed"] / cpave).round()
east["participants"] = east["participants"].astype("Int64")  # nullable int
east = east.drop(columns=["cpratio"])

# West: convert "Sep-2025" -> "2025-09" so all sources share one date format
west["month"] = pd.to_datetime(west["period"], format="%b-%Y").dt.strftime("%Y-%m")
west = west.drop(columns=["period"])

# Rename each source to the shared schema
east = east.rename(columns={
    "location": "center", "service_type": "program",
    "participants": "enrollments", "completed": "completions",
})
west = west.rename(columns={
    "site": "center", "program_name": "program",
    "enrolled": "enrollments", "completed_count": "completions",
})

# Enforce shared column order
SCHEMA = ["center", "month", "program", "enrollments", "completions"]
east, west, north = east[SCHEMA], west[SCHEMA], north[SCHEMA]

# Combine and verify the schema is what we expect before reporting
combined = pd.concat([east, west, north], ignore_index=True)
assert set(combined.columns) == set(SCHEMA), \
    f"Schema mismatch: {set(combined.columns) ^ set(SCHEMA)}"

# Summary reports via SQL against the in-memory DataFrame
summary_by_center = duckdb.sql("""
    SELECT center,
           SUM(enrollments) AS total_enrollments,
           SUM(completions) AS total_completions,
           SUM(completions) * 1.0 / SUM(enrollments) AS completion_rate
    FROM combined
    GROUP BY center
    ORDER BY center
""").df()

monthly_trend = duckdb.sql("""
    SELECT month,
           SUM(enrollments) AS total_enrollments
    FROM combined
    GROUP BY month
    ORDER BY month
""").df()

# Write both summaries to one Excel workbook
with pd.ExcelWriter(DATA / "report.xlsx") as writer:
    summary_by_center.to_excel(writer, sheet_name="Summary by Center", index=False)
    monthly_trend.to_excel(writer, sheet_name="Monthly Trend", index=False)

print(f"Wrote {DATA / 'report.xlsx'}")
