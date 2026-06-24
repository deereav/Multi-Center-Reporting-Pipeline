# Multi-Center Reporting Pipeline

A small Python pipeline that takes inconsistent monthly data from three
regional centers, normalizes it into a single schema, and produces a
standardized Excel report.

## Why this exists

Reporting across multiple sources usually breaks on the unglamorous part:
each source has its own column names, date formats, and quiet data quality
problems. Translating raw files into a clean shared schema — and proving
the schema is what you think it is — is what makes downstream reporting
trustworthy. This repo is a compact example of that work.

## The job

Three regional centers (East, West, North) submit monthly enrollment and
completion data. Each file is shaped differently. The pipeline:

1. Loads all three CSVs.
2. Fills missing values in East using a derived completion ratio.
3. Reformats West's date column from `Sep-2025` to `2025-09`.
4. Renames each source's columns to a shared schema.
5. Concatenates everything into a single combined table.
6. Generates two summary reports — by center and by month — using SQL
   (DuckDB) against the in-memory DataFrame.
7. Writes both reports as separate sheets in `report.xlsx`.

## Source schemas (before normalization)

| Source | Columns                                                        | Quirks                                   |
|--------|----------------------------------------------------------------|------------------------------------------|
| East   | `location`, `month`, `service_type`, `participants`, `completed` | Some `participants` values are missing.  |
| West   | `site`, `period`, `program_name`, `enrolled`, `completed_count` | `period` is `Mon-YYYY` format.           |
| North  | `center`, `month`, `program`, `enrollments`, `completions`     | Already clean; only reordered.           |

## Target schema (after normalization)

`center`, `month`, `program`, `enrollments`, `completions`

## How missing data is handled

East occasionally omits `participants` (enrollments). Rather than dropping
those rows or imputing a constant, the pipeline computes the
completion-to-participant ratio across the rows that *do* have both values,
then estimates the missing `participants` from each row's known
`completed` count divided by that average ratio. Simple, defensible, and
preserves every row.

## SQL inside Python (DuckDB)

The summary step uses DuckDB to run SQL directly against the combined
DataFrame, instead of pandas `groupby`. Both work; SQL is here on purpose,
to keep the reporting logic in the language an auditor or business analyst
can read.

## Repo layout

    data/         Source CSVs (east, west, north) and generated report
    pipeline.py   The pipeline

## Run it

    python pipeline.py

Output: `report.xlsx` with two sheets — `Summary by Center` and
`Monthly Trend`.

## Requirements

- Python 3.9+
- pandas, duckdb, openpyxl

Install:

    pip install pandas duckdb openpyxl

## Author

Daryl Reavis — SAS programmer focused on legacy SAS maintenance and
SAS-to-Python migration with output parity validation.

## License

MIT License — see LICENSE file for details.
