# Week 4 Capstone - End-to-End Sales Analysis

Dataset: Sample_data.xlsx (700 orders, Sep 2013 - Dec 2014).

## Run order (Python 3, pandas, matplotlib, xlsxwriter, reportlab, Pillow)
    cd code
    python 01_clean_explore.py <path-to-Sample_data.xlsx> ../data/clean_sales.csv
    python 02_sql_pandas_analysis.py      # SQLite queries + pandas cross-check
    python 03_charts.py                   # PNG charts
    python 04_excel_dashboard.py          # Excel dashboard (live formulas + native charts)
    python 05_report.py                   # PDF report

## Outputs
- outputs/Final_Report.pdf - findings, charts, recommendations
- outputs/Sales_Dashboard.xlsx - Dashboard, Data, Summary sheets
- data/clean_sales.csv - cleaned data (use as the Power BI / Tableau source)

## Power BI / Tableau build guide (same cleaned CSV)
1. Get Data > Text/CSV > data/clean_sales.csv. Set Discount_Band as text.
2. Measures: Margin % = DIVIDE(SUM(Profit), SUM(Sales)); Discount % = DIVIDE(SUM(Discounts), SUM(Gross_Sales)).
3. Visuals: KPI cards (Sales, Profit, Margin %); line chart Year_Month x Sales/Profit; bar Segment x Profit; matrix Segment x Discount_Band with Margin % (conditional colour); bar Product and Country.
4. Slicers: Year, Segment, Country, Product, Discount_Band.
5. Highlight: Enterprise has negative margin; discounts >4% make Enterprise orders loss-making.
