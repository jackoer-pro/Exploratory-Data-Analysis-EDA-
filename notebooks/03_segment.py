#%%
import pandas as pd
# load sales
sales = pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\sales.csv", parse_dates=["InvoiceDate"])
sales["Revenue"]=sales["Quantity"]*sales["UnitPrice"]
# load returns
returns=pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\returns.csv", parse_dates=["InvoiceDate"])
returns["ReturnValue"]= returns["Quantity"].abs() * returns["UnitPrice"]
# gross spend per customer
gross=sales.groupby("CustomerID")["Revenue"].sum()
# return value per customer
returned=returns.groupby("CustomerID")["ReturnValue"].sum()
# Net spend- fill 0 for customer who never returned anything
net_spend=(gross-returned).fillna(gross)
print("Gross vs Net comparison:")
print(f"Total gross spend : £{gross.sum():,.0f}")
print(f"Total returned    : £{returned.sum():,.0f}")
print(f"Total net spend   : £{net_spend.sum():,.0f}")
# %%
# Compare totals directly
total_returns_all        = returns["ReturnValue"].sum()
total_returns_with_custid = returns[returns["CustomerID"].notna()]["ReturnValue"].sum()
total_returned_in_net    = returned.sum()

print(f"All returns total          : £{total_returns_all:,.2f}")
print(f"Returns with CustomerID    : £{total_returns_with_custid:,.2f}")
print(f"Returned in net_spend calc : £{total_returned_in_net:,.2f}")
print(f"Gap 1 (all vs has custID)  : £{total_returns_all - total_returns_with_custid:,.2f}")
print(f"Gap 2 (custID vs net_spend): £{total_returns_with_custid - total_returned_in_net:,.2f}")
# %%
no_cust_returns=returns[returns["CustomerID"].isna()]
print(f"Returns with no CustomerID: {len(no_cust_returns)}")
print(f"Their value: £{no_cust_returns['ReturnValue'].sum():,.2f}")
print(no_cust_returns[['InvoiceNo','Description','Quantity','UnitPrice','CustomerID']].head(10))
# go directly to the excel file to investigate
# NOTE: £285K of returns have no CustomerID (anonymous + fee reversals)
# These are excluded from net_spend calculation — can't attribute to a customer
# Dashboard KPI uses full £897K for accurate business-level P&L
# RFM uses £611K net for accurate customer-level value scoring
# %%
reference_date=sales["InvoiceDate"].max()+pd.Timedelta(days=1)
rfm=sales.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x:(reference_date-x.max()).days),
    Frequency=("InvoiceNo",  lambda x: x.nunique()),
).reset_index()
# Merge net spend in separately
rfm = rfm.merge(
    net_spend.rename("Monetary").reset_index(),
    on="CustomerID",
    how="left"
)

print(rfm.head(10))
print(f"\nAverage net monetary: £{rfm['Monetary'].mean():,.2f}")
print(f"Average gross monetary was: £2,054")
# %%
# Rescore with net monetary
rfm["R"] = pd.qcut(rfm["Recency"].rank(method="first"),
                   q=5, labels=[5,4,3,2,1])
rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"),
                   q=5, labels=[1,2,3,4,5])
rfm["M"] = pd.qcut(rfm["Monetary"].rank(method="first"),
                   q=5, labels=[1,2,3,4,5])
def customer_segment(row):
    r=row["R"]
    f=row["F"]
    m=row["M"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champion"
    elif r>=3 and f>=3:
        return "Loyal"
    elif r>=4:
        return "New customer"
    elif m >= 4 and r <= 2 and f <= 1:
        return "Lost high value"
    elif m >= 4 and r <= 2:
        return "At risk"
    else:
        return "Normal"

rfm["R"] = rfm["R"].astype(int)
rfm["F"] = rfm["F"].astype(int)
rfm["M"] = rfm["M"].astype(int)

rfm["Seg"] = rfm.apply(customer_segment, axis=1)
print(rfm["Seg"].value_counts())
# %%
rfm.to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\segment.csv", index=False)

seg_summary = rfm.groupby("Seg").agg(
    Customers = ("CustomerID", "count"),
    Revenue   = ("Monetary",   "sum")
).reset_index()
seg_summary["Rev_pct"] = (seg_summary["Revenue"] /
                          seg_summary["Revenue"].sum() * 100).round(1)
seg_summary.to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\seg_summary.csv", index=False)

action_list = pd.concat([
    rfm[rfm["Seg"] == "At risk"].sort_values("Monetary", ascending=False),
    rfm[rfm["Seg"] == "Champion"].sort_values("Monetary", ascending=False)
])[["CustomerID","Seg","Recency","Frequency","Monetary"]]
action_list.to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\action_list.csv", index=False)

print("All 3 files resaved with net monetary.")
# LIMITATION: Net spend calculation is bounded by the dataset window
# Returns from purchases before Dec 2010 are excluded from net_spend
# In production: use 24-36 months of sales history to minimise this gap
# Current impact: £285K of returns unattributed (~3.2% of gross revenue)
# Acceptable for portfolio analysis — flag for real business deployment
# %%
