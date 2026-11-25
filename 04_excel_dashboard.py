"""Step 4 - Excel workbook: cleaned data, summary tables, native Excel charts, dashboard."""
import pandas as pd

df = pd.read_csv("../data/clean_sales.csv", keep_default_na=False, na_values=[""])
wb_path = "../outputs/Sales_Dashboard.xlsx"
w = pd.ExcelWriter(wb_path, engine="xlsxwriter", datetime_format="yyyy-mm-dd")
wb = w.book
hdr = wb.add_format({"bold": True, "bg_color": "#1F3A5F", "font_color": "white", "border": 1})
money = wb.add_format({"num_format": "$#,##0"}); pct = wb.add_format({"num_format": "0.0%"})
title = wb.add_format({"bold": True, "font_size": 18, "font_color": "#1F3A5F"})
kl = wb.add_format({"font_size": 10, "font_color": "#666666", "align": "center", "bg_color": "#EEF3F9", "top": 1})
kv = wb.add_format({"bold": True, "font_size": 16, "align": "center", "bg_color": "#EEF3F9", "num_format": "$#,##0.0,,\"M\"", "bottom": 1})
kp = wb.add_format({"bold": True, "font_size": 16, "align": "center", "bg_color": "#EEF3F9", "num_format": "0.0%", "bottom": 1})

dash = wb.add_worksheet("Dashboard")
df.to_excel(w, sheet_name="Data", index=False)
ds = w.sheets["Data"]; ds.freeze_panes(1, 0); ds.autofilter(0, 0, len(df), df.shape[1] - 1); ds.set_column(0, df.shape[1] - 1, 15)
n = len(df) + 1
col = {c: chr(65 + i) for i, c in enumerate(df.columns)}
rng = lambda c: f"Data!${col[c]}$2:${col[c]}${n}"

# ---- summary sheet with live SUMIFS formulas ----
sm = wb.add_worksheet("Summary")
def table(r0, name, key, items):
    sm.write(r0, 0, name, hdr)
    for j, h in enumerate(["Sales", "Profit", "Margin"]): sm.write(r0, 1 + j, h, hdr)
    for i, it in enumerate(items, 1):
        r = r0 + i
        sm.write(r, 0, it)
        sub = df[df[key] == it]; sv, pv = sub.Sales.sum(), sub.Profit.sum()   # cached values for viewers that don't recalc
        sm.write_formula(r, 1, f'=SUMIFS({rng("Sales")},{rng(key)},$A{r+1})', money, sv)
        sm.write_formula(r, 2, f'=SUMIFS({rng("Profit")},{rng(key)},$A{r+1})', money, pv)
        sm.write_formula(r, 3, f'=IFERROR(C{r+1}/B{r+1},0)', pct, pv / sv if sv else 0)
    return r0, r0 + len(items)

segs = ["Government", "Small Business", "Channel Partners", "Midmarket", "Enterprise"]
bands = ["None", "Low", "Medium", "High"]
prods = list(df.groupby("Product").Profit.sum().sort_values(ascending=False).index)
ctys = list(df.groupby("Country").Profit.sum().sort_values(ascending=False).index)
mons = sorted(df.Year_Month.unique())
T = {}
T["seg"] = table(0, "Segment", "Segment", segs)
T["band"] = table(8, "Discount_Band", "Discount_Band", bands)
T["prod"] = table(15, "Product", "Product", prods)
T["cty"] = table(24, "Country", "Country", ctys)
T["mon"] = table(32, "Year_Month", "Year_Month", mons)
sm.set_column(0, 0, 18); sm.set_column(1, 3, 15)

def chart(kind, tkey, name, ycols, anchor, size=(480, 300), colors=("#2F6DB5", "#1F9E89"), fmt=None):
    r0, r1 = T[tkey]; ch = wb.add_chart({"type": kind})
    for k, cidx in enumerate(ycols):
        ch.add_series({"name": ["Summary", r0, cidx], "categories": ["Summary", r0 + 1, 0, r1, 0],
                       "values": ["Summary", r0 + 1, cidx, r1, cidx], "fill": {"color": colors[k]}, "line": {"color": colors[k]}})
    ch.set_title({"name": name, "name_font": {"size": 12}}); ch.set_legend({"position": "bottom"} if len(ycols) > 1 else {"none": True})
    ch.set_y_axis({"num_format": fmt or '$#,##0.0,,"M"', "major_gridlines": {"visible": True, "line": {"color": "#DDDDDD"}}})
    ch.set_size({"width": size[0], "height": size[1]}); dash.insert_chart(anchor, ch)

# ---- dashboard ----
dash.hide_gridlines(2); dash.set_column(0, 20, 11)
dash.write("A1", "Sales Performance Dashboard  |  Sep 2013 - Dec 2014", title)
kpis = [("Total Sales", f"=SUM({rng('Sales')})", kv, df.Sales.sum()), ("Total Profit", f"=SUM({rng('Profit')})", kv, df.Profit.sum()),
        ("Profit Margin", f"=SUM({rng('Profit')})/SUM({rng('Sales')})", kp, df.Profit.sum() / df.Sales.sum()), ("Discounts Given", f"=SUM({rng('Discounts')})", kv, df.Discounts.sum()),
        ("Units Sold", f"=SUM({rng('Units_Sold')})", wb.add_format({"bold": True, "font_size": 16, "align": "center", "bg_color": "#EEF3F9", "num_format": "#,##0", "bottom": 1}), df.Units_Sold.sum())]
for i, (lab, f, fm, val) in enumerate(kpis):
    c = i * 4
    dash.merge_range(2, c, 2, c + 3, lab, kl); dash.merge_range(3, c, 3, c + 3, "", fm); dash.write_formula(3, c, f, fm, val)
dash.set_row(3, 30)
chart("line", "mon", "Monthly Sales vs Profit", [1, 2], "A6", (640, 300))
chart("column", "seg", "Sales & Profit by Segment", [1, 2], "L6", (640, 300))
chart("column", "band", "Profit by Discount Band", [2], "A22", (400, 280), ("#D1495B",))
chart("column", "prod", "Sales & Profit by Product", [1, 2], "H22", (440, 280))
chart("bar", "cty", "Profit by Country", [2], "O22", (430, 280))
dash.write("A38", "Key insight: Enterprise segment loses money (-3.1% margin); all 58 loss-making orders are Enterprise with Medium/High discounts.",
           wb.add_format({"bold": True, "font_color": "#D1495B"}))
w.close(); print("saved", wb_path)
