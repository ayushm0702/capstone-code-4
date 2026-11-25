"""Step 2 - Analyse with SQL (SQLite) and cross-check with pandas."""
import sqlite3, json
import pandas as pd

df = pd.read_csv("../data/clean_sales.csv", keep_default_na=False, na_values=[""])
con = sqlite3.connect("../data/sales.db")
df.to_sql("sales", con, if_exists="replace", index=False)

Q = {
"kpi": """SELECT ROUND(SUM(Gross_Sales)) gross, ROUND(SUM(Discounts)) discounts, ROUND(SUM(Sales)) sales,
          ROUND(SUM(COGS)) cogs, ROUND(SUM(Profit)) profit, ROUND(SUM(Profit)*100.0/SUM(Sales),2) margin_pct,
          SUM(Units_Sold) units, COUNT(*) orders FROM sales""",
"by_segment": """SELECT Segment, ROUND(SUM(Sales)) sales, ROUND(SUM(Profit)) profit,
          ROUND(SUM(Profit)*100.0/SUM(Sales),2) margin_pct, ROUND(SUM(Discounts)*100.0/SUM(Gross_Sales),2) discount_pct
          FROM sales GROUP BY Segment ORDER BY profit DESC""",
"by_country": """SELECT Country, ROUND(SUM(Sales)) sales, ROUND(SUM(Profit)) profit,
          ROUND(SUM(Profit)*100.0/SUM(Sales),2) margin_pct FROM sales GROUP BY Country ORDER BY profit DESC""",
"by_product": """SELECT Product, ROUND(SUM(Units_Sold)) units, ROUND(SUM(Sales)) sales, ROUND(SUM(Profit)) profit,
          ROUND(SUM(Profit)*100.0/SUM(Sales),2) margin_pct FROM sales GROUP BY Product ORDER BY profit DESC""",
"by_discount": """SELECT Discount_Band, COUNT(*) orders, ROUND(SUM(Sales)) sales, ROUND(SUM(Profit)) profit,
          ROUND(SUM(Profit)*100.0/SUM(Sales),2) margin_pct, ROUND(AVG(Units_Sold)) avg_units
          FROM sales GROUP BY Discount_Band ORDER BY margin_pct DESC""",
"by_year": """SELECT Year, ROUND(SUM(Sales)) sales, ROUND(SUM(Profit)) profit, COUNT(DISTINCT Year_Month) months,
          ROUND(SUM(Sales)/COUNT(DISTINCT Year_Month)) sales_per_month FROM sales GROUP BY Year""",
"monthly": """SELECT Year_Month, ROUND(SUM(Sales)) sales, ROUND(SUM(Profit)) profit FROM sales GROUP BY Year_Month ORDER BY Year_Month""",
"loss_making": """SELECT Segment, Product, Country, Discount_Band, ROUND(Sales) sales, ROUND(Profit) profit, Year_Month
          FROM sales WHERE Profit < 0 ORDER BY Profit LIMIT 10""",
"loss_summary": """SELECT Segment, Discount_Band, COUNT(*) loss_orders, ROUND(SUM(Profit)) total_loss
          FROM sales WHERE Profit < 0 GROUP BY Segment, Discount_Band""",
"seg_product_margin": """SELECT Segment, Product, ROUND(SUM(Profit)*100.0/SUM(Sales),1) margin_pct, ROUND(SUM(Profit)) profit
          FROM sales GROUP BY Segment, Product ORDER BY profit DESC""",
"top_combos": """SELECT Country, Product, ROUND(SUM(Profit)) profit FROM sales GROUP BY Country, Product ORDER BY profit DESC LIMIT 5""",
}
res = {k: pd.read_sql(q, con) for k, q in Q.items()}
for k, v in res.items():
    print(f"\n== {k} ==\n{v.to_string(index=False)}")
    v.to_csv(f"../data/result_{k}.csv", index=False)

# pandas cross-check
assert round(df.Profit.sum()) == res["kpi"].profit[0], "SQL vs pandas profit mismatch"
assert round(df.Sales.sum()) == res["kpi"].sales[0]
print("\nPandas cross-check OK")

# Pandas-only analysis: Which cuts have a negative/low margin, and correlation
print("\nCorrelation with Profit:\n", df[["Units_Sold","Discounts","Sales","COGS","Profit"]].corr()["Profit"].round(2).to_string())
yoy = df.groupby(["Year","Month_Number"]).Sales.sum().unstack(0)
print("\nSame-month YoY (months in both years):")
both = yoy.dropna(); print((both[2014]/both[2013]-1).round(3).to_string())
con.close()
