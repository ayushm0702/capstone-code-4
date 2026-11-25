"""Step 1 - Clean and explore the dataset."""
import sys
import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else "Sample_data.xlsx"
OUT = sys.argv[2] if len(sys.argv) > 2 else "../data/clean_sales.csv"

df = pd.read_excel(SRC, keep_default_na=False, na_values=[""])
print("Raw shape:", df.shape)

# 1. tidy column names (' Sales' has a leading space)
df.columns = df.columns.str.strip().str.replace(" ", "_")

# 2. 'None' discount band was being parsed as missing -> keep it as a real category
df["Discount_Band"] = df["Discount_Band"].fillna("None").astype(str)

# 3. types
df["Units_Sold"] = df["Units_Sold"].astype(float)  # some rows have .5 units; keep as-is
df["Date"] = pd.to_datetime(df["Date"])
df["Country"] = df["Country"].replace({"United States of America": "USA"})

# 4. integrity checks
checks = {
    "missing values": int(df.isna().sum().sum()),
    "duplicate rows": int(df.duplicated().sum()),
    "Gross - Discounts != Sales": int(((df.Gross_Sales - df.Discounts - df.Sales).abs() > 1).sum()),
    "Sales - COGS != Profit": int(((df.Sales - df.COGS - df.Profit).abs() > 1).sum()),
    "Units*SalePrice != Gross": int(((df.Units_Sold * df.Sale_Price - df.Gross_Sales).abs() > 1).sum()),
    "negative profit rows": int((df.Profit < 0).sum()),
    "date/month mismatch": int((df.Date.dt.month != df.Month_Number).sum()),
}
for k, v in checks.items():
    print(f"  {k}: {v}")

# 5. derived fields
df["Profit_Margin_%"] = (df.Profit / df.Sales * 100).round(2)
df["Discount_%_of_Gross"] = (df.Discounts / df.Gross_Sales * 100).round(2)
df["Quarter"] = "Q" + df.Date.dt.quarter.astype(str)
df["Year_Month"] = df.Date.dt.to_period("M").astype(str)

# 6. quick EDA
print("\nDate range:", df.Date.min().date(), "->", df.Date.max().date())
print(df[["Units_Sold", "Gross_Sales", "Discounts", "Sales", "COGS", "Profit", "Profit_Margin_%"]].describe().round(1).T)
for c in ["Segment", "Country", "Product", "Discount_Band", "Year"]:
    print(f"\n{c}:\n{df[c].value_counts().to_string()}")

# outliers (IQR) on Sales
q1, q3 = df.Sales.quantile([.25, .75]); iqr = q3 - q1
out = df[(df.Sales > q3 + 1.5 * iqr) | (df.Sales < q1 - 1.5 * iqr)]
print(f"\nSales outliers (IQR rule): {len(out)} rows (kept - genuine large deals)")

df.to_csv(OUT, index=False)
print("\nSaved", OUT, df.shape)
