# Multi-Center-Reporting-Pipeline
A Python pipeline that consolidates monthly enrollment and completion data from three regional centers — each submitting data in a different format — and produces a standardized Excel report.

The Problem
Three regional centers (North, East, West) each track program enrollment and completions, but submit their data independently. The result is three CSV files with:
•	Different column names for the same concepts (participants vs enrolled vs enrollments)
•	Different date formats (2024-01 vs Jan-2024)
•	Occasional missing values
The goal is a single Excel report with consistent summaries that management can rely on each month.

The Approach
1.	Ingest each center's CSV separately, since each has its own schema
2.	Clean — handle missing values by estimating from the completion ratio, standardize date formats, drop helper columns
3.	Standardize column names and order across all three sources
4.	Combine into a single data frame
5.	Summarize using SQL (via DuckDB) — one query for the by-center summary, one for the monthly trend
6.	Write to Excel with two sheets

Key Design Decisions
Estimating missing enrollment records. East had a missing enrollment value. Rather than dropping the row or filling with zero, I calculated the average completions-to-enrollments ratio across East's other records and used that to back-calculate a plausible enrollment number. This preserves the row in the summary while being transparent about the estimate.
SQL via DuckDB. I chose SQL because the aggregation logic reads more naturally and more universally recognized in SQL. DuckDB lets you query a pandas data frame directly without setting up a database.
Two-pass cleaning. Each center gets its own cleaning step before standardization, because the issues are different — East needs imputation, West needs date conversion, North is already clean. Trying to handle all three in one generic step would be more code, not less.

Files
•	pipeline.py — main script
•	data/east.csv, data/west.csv, data/north.csv — sample input data
•	report.xlsx — generated output

Requirements
pandas
duckdb
openpyxl - embedded in ExcelWriter

Running
python pipeline.py
Reads from the data/ folder, writes report.xlsx to the project directory.
