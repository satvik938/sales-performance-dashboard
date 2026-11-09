"""Generate the synthetic raw data for the Sales Performance dashboard.

All records are randomly generated with a fixed seed so results are reproducible.
No real company, customer or employee data is used.

Run from the repository root:  python generate_data.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path(__file__).resolve().parent  # CSVs are written next to this script
rng = np.random.default_rng(7)
months = pd.date_range("2025-11-01", "2026-10-01", freq="MS")

# ---------- 2. Sales Performance ----------
regions={"South Central":1.25,"Midwest":1.0,"Southeast":0.95,"Mountain West":0.6,"Northeast":0.8}
cats={"Industrial Supplies":(320,0.31),"Safety Equipment":(145,0.38),"Packaging":(90,0.27),"Tools & Hardware":(210,0.34),"Electrical":(260,0.29)}
channels=["Direct Sales","E-commerce","Distributor"]
reps=[f"Rep {c}" for c in "ABCDEFGHIJKL"]
srows=[];oid=500000
for m_i,m in enumerate(months):
    growth=1+0.012*m_i
    seas=1+0.12*np.cos((m.month-3)/12*2*np.pi)
    for r,rw in regions.items():
        n=int(rng.normal(230,15)*rw*growth*seas)
        for _ in range(n):
            c=rng.choice(list(cats)); base,margin=cats[c]
            ch=rng.choice(channels,p=[.45,.35,.2])
            qty=int(rng.integers(1,25)); price=base*rng.normal(1,0.1)
            disc=rng.choice([0,0.05,0.1,0.15],p=[.55,.25,.15,.05])
            rev=qty*price*(1-disc)
            srows.append(dict(order_id=f"OR{oid}",month=m.strftime("%Y-%m"),region=r,category=c,channel=ch,
              rep=rng.choice(reps),quantity=qty,revenue=round(rev,2),
              gross_profit=round(rev*(margin-disc*0.8)*rng.normal(1,0.05),2),
              new_customer=int(rng.random()<0.18)))
            oid+=1
pd.DataFrame(srows).to_csv(RAW / "sales_orders.csv",index=False)
targets=[dict(month=m.strftime("%Y-%m"),target=round(2.68e6*(1+0.01*i)*(1+0.12*np.cos((m.month-3)/12*2*np.pi)),-3)) for i,m in enumerate(months)]
pd.DataFrame(targets).to_csv(RAW / "sales_targets.csv",index=False)
print("Raw data written to", RAW)
