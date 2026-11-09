"""Clean and aggregate the raw data into the summary tables the dashboard reads.

Outputs:
  summary CSVs          one CSV per dashboard table
  data.js                the same tables bundled for index.html (so it also opens from disk)

Headline KPIs compare the latest 3 months (Aug-Oct 2026) with the prior 3 months (May-Jul 2026).
Run from the repository root:  python build_metrics.py
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent  # all files live in the repository root
RAW = ROOT
OUT = ROOT
CUR = ["2026-08", "2026-09", "2026-10"]
PRV = ["2026-05", "2026-06", "2026-07"]

# ---------- Sales ----------
o=pd.read_csv(RAW / "sales_orders.csv"); t=pd.read_csv(RAW / "sales_targets.csv")
sm=o.groupby("month").agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum"),orders=("order_id","count"),new_customers=("new_customer","sum")).reset_index().merge(t)
sm["margin_pct"]=sm.gross_profit/sm.revenue*100; sm["attainment_pct"]=sm.revenue/sm.target*100; sm["avg_order_value"]=sm.revenue/sm.orders
sm.round(1).to_csv(OUT / "sales_monthly.csv",index=False)
def sk(m):
    d=sm[sm.month.isin(m)]; return d.revenue.sum(),d.gross_profit.sum()/d.revenue.sum()*100,d.revenue.sum()/d.orders.sum(),d.revenue.sum()/d.target.sum()*100,d.new_customers.sum()
cr,cm,ca,ct,cn=sk(CUR); pr,pm,pa,pt,pn=sk(PRV)
pd.DataFrame([dict(window="Aug–Oct 2026",compare="May–Jul 2026",revenue=round(cr),revenue_chg_pct=round((cr/pr-1)*100,1),
  margin_pct=round(cm,1),margin_chg_pts=round(cm-pm,1),avg_order_value=round(ca,0),aov_chg_pct=round((ca/pa-1)*100,1),
  attainment_pct=round(ct,1),attainment_chg_pts=round(ct-pt,1),new_customers=int(cn),new_customers_chg_pct=round((cn/pn-1)*100,1),
  revenue_12m=round(sm.revenue.sum()),target_12m=round(sm.target.sum()),months_on_target=int((sm.attainment_pct>=100).sum()))]).to_csv(OUT / "sales_kpis.csv",index=False)
def grp(col):
    g=o.groupby(col).agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum"),orders=("order_id","count")).reset_index()
    g["margin_pct"]=g.gross_profit/g.revenue*100; g["share_pct"]=g.revenue/g.revenue.sum()*100
    return g.sort_values("revenue",ascending=False).round(1)
grp("region").to_csv(OUT / "sales_regions.csv",index=False)
grp("category").to_csv(OUT / "sales_categories.csv",index=False)
grp("channel").to_csv(OUT / "sales_channels.csv",index=False)
for f,cols in [("sales_monthly.csv",["revenue","gross_profit","target"]),("sales_regions.csv",["revenue","gross_profit"]),
               ("sales_categories.csv",["revenue","gross_profit"]),("sales_channels.csv",["revenue","gross_profit"])]:
    d=pd.read_csv(OUT/f); d[cols]=d[cols].round().astype(int); d.to_csv(OUT/f,index=False)

# Bundle tables for the dashboard page
DATASETS = {"kpis": "sales_kpis.csv", "monthly": "sales_monthly.csv", "regions": "sales_regions.csv", "categories": "sales_categories.csv", "channels": "sales_channels.csv"}
bundle = {k: (OUT / v).read_text() for k, v in DATASETS.items()}
(ROOT / "data.js").write_text("window.DASH_DATA = " + json.dumps(bundle, indent=1) + ";\n")
print("Processed tables written to", OUT)
