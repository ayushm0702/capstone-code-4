"""Step 3 - Charts (PNG) used in the report and Excel dashboard."""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("../data/clean_sales.csv", keep_default_na=False, na_values=[""])
OUT = "../outputs/charts/"
C = {"blue": "#2F6DB5", "teal": "#1F9E89", "red": "#D1495B", "grey": "#8C8C8C"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
M = lambda x, p=None: f"${x/1e6:.0f}M" if abs(x) >= 1e6 else f"${x/1e3:.0f}K"
fmt = plt.FuncFormatter(M)

def save(name):
    plt.tight_layout(); plt.savefig(OUT + name, dpi=160); plt.close()

# 1 monthly trend
m = df.groupby("Year_Month")[["Sales", "Profit"]].sum()
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(m.index, m.Sales, marker="o", color=C["blue"], label="Sales")
ax.plot(m.index, m.Profit, marker="o", color=C["teal"], label="Profit")
ax.yaxis.set_major_formatter(fmt); ax.set_title("Monthly Sales and Profit (Sep 2013 - Dec 2014)", loc="left", weight="bold")
plt.xticks(rotation=60, ha="right"); ax.legend(frameon=False); save("01_monthly_trend.png")

# 2 profit & margin by segment
s = df.groupby("Segment").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).sort_values("Profit")
s["m"] = s.Profit / s.Sales * 100
fig, ax = plt.subplots(figsize=(8, 4))
b = ax.barh(s.index, s.Profit, color=[C["red"] if v < 0 else C["blue"] for v in s.Profit])
for r, mg in zip(b, s.m):
    ax.text(r.get_width() + (3e5 if r.get_width() >= 0 else -3e5), r.get_y() + r.get_height()/2, f"{mg:.1f}% margin",
            va="center", ha="left" if r.get_width() >= 0 else "right", fontsize=9)
ax.xaxis.set_major_formatter(fmt); ax.set_xlim(-2.5e6, 14e6); ax.axvline(0, color="black", lw=.6)
ax.set_title("Profit by Segment: Enterprise is losing money", loc="left", weight="bold"); save("02_segment_profit.png")

# 3 margin by discount band
d = df.groupby("Discount_Band").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reindex(["None", "Low", "Medium", "High"])
d["m"] = d.Profit / d.Sales * 100
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(d.index, d.m, color=[C["teal"], C["blue"], C["blue"], C["red"]])
for i, v in enumerate(d.m): ax.text(i, v + .4, f"{v:.1f}%", ha="center")
ax.set_ylabel("Profit margin %"); ax.set_title("Heavier discounts, thinner margins", loc="left", weight="bold"); save("03_discount_margin.png")

# 4 heatmap segment x discount band margin
h = df.groupby(["Segment", "Discount_Band"]).apply(lambda g: g.Profit.sum()/g.Sales.sum()*100, include_groups=False).unstack()[["None", "Low", "Medium", "High"]]
fig, ax = plt.subplots(figsize=(7, 3.8))
im = ax.imshow(h.values, cmap="RdYlGn", vmin=-30, vmax=40, aspect="auto")
ax.set_xticks(range(4)); ax.set_xticklabels(h.columns); ax.set_yticks(range(len(h))); ax.set_yticklabels(h.index)
for i in range(h.shape[0]):
    for j in range(h.shape[1]): ax.text(j, i, f"{h.values[i, j]:.1f}%", ha="center", va="center", fontsize=9)
ax.set_title("Profit margin: Segment x Discount band", loc="left", weight="bold"); save("04_heatmap_margin.png")

# 5 product
p = df.groupby("Product").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).sort_values("Profit", ascending=False)
fig, ax = plt.subplots(figsize=(8, 4)); x = range(len(p))
ax.bar([i - .2 for i in x], p.Sales, .4, label="Sales", color=C["blue"]); ax.bar([i + .2 for i in x], p.Profit, .4, label="Profit", color=C["teal"])
ax.set_xticks(list(x)); ax.set_xticklabels(p.index); ax.yaxis.set_major_formatter(fmt); ax.legend(frameon=False)
ax.set_title("Sales and Profit by Product", loc="left", weight="bold"); save("05_product.png")

# 6 country
c = df.groupby("Country").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).sort_values("Profit")
c["m"] = c.Profit / c.Sales * 100
fig, ax = plt.subplots(figsize=(7, 3.8)); ax.barh(c.index, c.Profit, color=C["blue"])
for i, (pv, mg) in enumerate(zip(c.Profit, c.m)): ax.text(pv + 5e4, i, f"{mg:.1f}%", va="center")
ax.xaxis.set_major_formatter(fmt); ax.set_title("Profit by Country (label = margin)", loc="left", weight="bold"); save("06_country.png")

# 7 enterprise discount effect: discount % vs margin scatter
e = df[df.Segment == "Enterprise"]
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.scatter(e["Discount_%_of_Gross"], e["Profit_Margin_%"], c=[C["red"] if v < 0 else C["teal"] for v in e["Profit_Margin_%"]], alpha=.7)
ax.axhline(0, color="black", lw=.6); ax.set_xlabel("Discount as % of gross sales"); ax.set_ylabel("Profit margin %")
ax.set_title("Enterprise: every order discounted >4% loses money", loc="left", weight="bold", fontsize=10); save("07_enterprise_scatter.png")
print("charts done")
