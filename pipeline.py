import pandas as pd
import duckdb
east = pd.read_csv("data/east.csv")
west = pd.read_csv("data/west.csv")
north = pd.read_csv("data/north.csv")
#Clean east.csv - Use average ratio for calculationg missing data
east["cpratio"] = east["completed"] / east["participants"]
cpave = (east["cpratio"]).mean()
east.loc[east["participants"].isna(), "participants"] = round(east["completed"] / cpave)
#Clean west.csv - Convert the date to the same format as other datasets
west["month"] = pd.to_datetime(west["period"], format="%b-%Y").dt.strftime("%Y-%m")
#Drop extra columns
east = east.drop(columns=["cpratio"])
west = west.drop(columns= ["period"])
#Rename columns so there is name consistency across all datasets
east = east.rename(columns={"location": "center", "participants": "enrollments", "service_type": "program", "completed":"completions"})
west = west.rename(columns={"site": "center", "enrolled": "enrollments", "program_name": "program", "completed_count": "completions"})
#Reorder columns so that there is column order consistency across all datasets
west = west[["center", "month", "program", "enrollments", "completions"]]
north = north[["center", "month", "program", "enrollments", "completions"]]
#Combine the datasets in one file
combined = pd.concat([east, west, north], ignore_index=True)
#Summarize the data using SQL and put the results back into pandas
#SQL Output to Excel
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
#Write the summary reports out to Excel
with pd.ExcelWriter("report.xlsx") as writer:
    summary_by_center.to_excel(writer, sheet_name="Summary by Center", index=False)
    monthly_trend.to_excel(writer, sheet_name="Monthly Trend", index=False)
