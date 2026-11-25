"""Step 5 - Compile the final PDF report (charts, findings, recommendations)."""
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak

df = pd.read_csv("../data/clean_sales.csv", keep_default_na=False, na_values=[""])
CH = "../outputs/charts/"
tot = dict(sales=df.Sales.sum(), profit=df.Profit.sum(), disc=df.Discounts.sum(), units=df.Units_Sold.sum())
ent = df[df.Segment == "Enterprise"]; loss = df[df.Profit < 0]
gov = df[df.Segment == "Government"]
M = lambda v: f"{'-' if v<0 else ''}${abs(v)/1e6:,.1f}M"; K = lambda v: f"{'-' if v<0 else ''}${abs(v)/1e3:,.0f}K"
assert set(loss.Segment) == {"Enterprise"}

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=colors.HexColor("#1F3A5F"), fontSize=18)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=colors.HexColor("#1F3A5F"), fontSize=13)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10, leading=14)
SM = ParagraphStyle("SM", parent=B, fontSize=8.5, textColor=colors.grey)
img = lambda f, w=15: Image(CH + f, width=w * cm, height=w * cm * (lambda i: i[1] / i[0])(__import__("PIL.Image", fromlist=["x"]).open(CH + f).size))
S = []
P = lambda t, st=B: S.append(Paragraph(t, st))
bullets = lambda items: [S.append(Paragraph("&bull; " + t, B)) for t in items]

P("End-to-End Sales Analysis Case Study", H1)
P("Data Analyst Course - Week 4 Capstone &nbsp;|&nbsp; Dataset: 700 orders, 5 segments, 5 countries, 6 products, Sep 2013 - Dec 2014", SM)
S.append(Spacer(1, 8))

P("1. Executive summary", H2)
P(f"The business generated <b>{M(tot['sales'])}</b> in net sales and <b>{M(tot['profit'])}</b> profit "
  f"(<b>{tot['profit']/tot['sales']:.1%}</b> margin) after <b>{M(tot['disc'])}</b> of discounts. Growth is healthy, but profit is concentrated "
  f"and one segment is destroying value:")
bullets([
    f"<b>Enterprise loses money</b>: {M(ent.Sales.sum())} of sales at a {ent.Profit.sum()/ent.Sales.sum():.1%} margin ({K(ent.Profit.sum())} total). "
    f"All {len(loss)} loss-making orders in the dataset are Enterprise orders ({K(loss.Profit.sum())} of losses).",
    f"<b>Discounts above 4% are the trigger</b>: Enterprise COGS is 96% of gross sales, so every Enterprise order discounted more than 4% lost money; none at 4% or less did.",
    f"<b>Government drives profit</b>: {gov.Profit.sum()/tot['profit']:.0%} of total profit ({M(gov.Profit.sum())}) at a {gov.Profit.sum()/gov.Sales.sum():.1%} margin.",
    "<b>Heavy discounting erodes margin everywhere</b>: margin falls from 21.9% (no discount) to 9.1% (High band), with no increase in units per order.",
])

P("2. Approach", H2)
bullets([
    "<b>Clean &amp; explore (Python/pandas)</b>: standardised column names, fixed 'None' discount band being read as missing, checked identities "
    "(Gross - Discounts = Sales; Sales - COGS = Profit; Units x Price = Gross) - all hold, no duplicates, no true missing values. Added margin, discount %, quarter fields.",
    "<b>Analyse (SQL + pandas)</b>: loaded into SQLite, ran aggregate queries by segment, country, product, discount band, and month; cross-checked totals against pandas.",
    "<b>Visualise</b>: Excel dashboard (live SUMIFS formulas and native charts), plus Python charts below. A Power BI / Tableau build guide is included in the README using the same cleaned CSV.",
])

P("3. KPIs", H2)
kt = Table([["Net sales", "Profit", "Margin", "Discounts", "Units sold"],
            [M(tot["sales"]), M(tot["profit"]), f"{tot['profit']/tot['sales']:.1%}", M(tot["disc"]), f"{tot['units']:,.0f}"]], colWidths=[3.4 * cm] * 5)
kt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTSIZE", (0, 1), (-1, 1), 13), ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                        ("BOX", (0, 0), (-1, -1), .5, colors.grey), ("TOPPADDING", (0, 1), (-1, 1), 8), ("BOTTOMPADDING", (0, 1), (-1, 1), 8)]))
S.append(kt); S.append(Spacer(1, 8))
S.append(img("01_monthly_trend.png", 15.5))
P("Sales are spiky with peaks in June, October and December. 2013 covers only Sep-Dec, so compare like-for-like months: "
  "Sep +43%, Oct +33%, Dec +124% year over year, Nov -26%. Treat the full-year jump (2013 vs 2014) as a coverage artefact, not growth.")
S.append(PageBreak())

P("4. Findings", H2)
P("<b>4.1 Segment: Enterprise is the problem, Channel Partners the opportunity</b>", B)
S.append(img("02_segment_profit.png", 14))
P("Government and Small Business generate 80% of net sales. Small Business is high-volume but thin (9.8% margin). "
  "Channel Partners earn a 73% margin but are only 1.5% of sales, which suggests under-exploited headroom.")
S.append(img("04_heatmap_margin.png", 13))
P("Enterprise is red in the Medium and High bands and barely positive otherwise (1.6% Low, 4.0% None). Small Business falls from 14.5% (Low) to 4.7% (High).")
S.append(PageBreak())
P("<b>4.2 Discounting</b>", B)
S.append(img("03_discount_margin.png", 10))
S.append(img("07_enterprise_scatter.png", 11))
P("Orders in the High band have the same average size as undiscounted ones (about 1,600 units), so the extra discount is not buying volume.")
P("<b>4.3 Product and country</b>", B)
S.append(img("05_product.png", 12))
S.append(img("06_country.png", 11))
P("Paseo is the largest product (28% of both sales and profit). Velo has the lowest margin (12.6%). France and Germany have the best margins (about 15.6%); USA has the weakest (12.0%) despite the highest sales.")
S.append(PageBreak())

P("5. Recommendations", H2)
bullets([
    f"<b>Cap Enterprise discounts at 4% or reprice Enterprise.</b> Removing the discount on the {len(loss)} loss-making orders recovers at least {K(-loss.Profit.sum())} "
    f"(~{-loss.Profit.sum()/tot['profit']:.1%} of total profit) before any change in price.",
    "<b>Introduce discount approval tiers</b> for Small Business: High-band orders return 4.7% margin vs 14.5% for Low, with no volume benefit.",
    "<b>Invest in Channel Partners and Midmarket</b>, which earn 73% and 28% margins on small sales bases.",
    "<b>Protect Government</b>: it carries two-thirds of profit, so a single contract loss would be material; diversify accordingly.",
    "<b>Plan inventory and staffing around Jun/Oct/Dec peaks</b> and investigate the November decline.",
    "<b>Review USA pricing and Velo cost</b>, the lowest-margin country and product.",
])
P("6. Limitations", H2)
P("Sample dataset: 700 rows, 16 months, no customer or cost-driver detail. 2013 is a partial year. Discount band is a category, so the effect of exact discount rates is shown only for Enterprise, where the percentage is available per order. Findings describe correlation, not tested causation.", B)

SimpleDocTemplate("../outputs/Final_Report.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                  title="Sales Analysis Case Study").build(S)
print("report saved")
