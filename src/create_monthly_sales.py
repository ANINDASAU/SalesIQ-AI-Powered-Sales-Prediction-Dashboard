
from pathlib import Path
import pandas as pd

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "Online Retail.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "monthly_sales.csv"

print("Reading Excel file...")

# 1. Load Excel data
df = pd.read_excel(INPUT_FILE)

print("Original rows:", len(df))

# 2. Clean source records consistently with the dashboard pipeline.
from src.preprocessing import clean_sales

df = clean_sales(df)

# 3. Aggregate revenue by month.
df["Month"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()

monthly_sales = (
    df.groupby("Month", as_index=False)["Revenue"]
    .sum()
)

monthly_sales["Month"] = monthly_sales["Month"].dt.strftime("%Y-%m-%d")

# 9. Create the output folder if it doesn't exist
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# 10. Save the CSV file
monthly_sales.to_csv(OUTPUT_FILE, index=False)

print("\nMonthly sales created successfully!")
print("Saved to:", OUTPUT_FILE)
print("\nFirst 5 months:")
print(monthly_sales.head())
print("\nTotal months:", len(monthly_sales))
