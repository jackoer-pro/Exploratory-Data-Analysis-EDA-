# %%
import pandas as pd
# %%
sales = pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\sales.csv", parse_dates=["InvoiceDate"])
sales["Revenue"]=sales["Quantity"]*sales["UnitPrice"]
print(sales["Revenue"].describe())
# %%
sales["Month"]= sales["InvoiceDate"].dt.to_period("M")
monthly_revenue= sales.groupby("Month")["Revenue"].sum()
print(monthly_revenue)
# %%
import matplotlib.pyplot as plt
monthly_revenue.plot(
    figsize=(12,4),
    marker="o",
    color="steelblue"
)
plt.ticklabel_format(style='plain', axis='y')
plt.title("Monthly revenue — when does money come in?")
plt.ylabel("Revenue (£)")
plt.tight_layout()
plt.show()
# Insight: peak month is November
# Action: stock more products on October
# %%
# 10 product with the highest revenue
mask_postage=sales["Description"]=="POSTAGE"
mask_manual=sales["Description"]=="Manual"
mask_dotcom=sales["Description"]=="DOTCOM POSTAGE"
mask_exclude = mask_postage | mask_manual | mask_dotcom
sales_product=sales[mask_exclude==False]
product_revenue=sales_product.groupby("Description")["Revenue"].sum()
top10_revenue = product_revenue.nlargest(10)
print(top10_revenue)

plt.figure(figsize=(10, 8))
top10_revenue.plot(kind='barh', color='skyblue')

plt.title('Top 10 Products by Revenue', fontsize=14)
plt.xlabel("Total Revenue")
plt.tight_layout()
plt.show()
# INSIGHT: Postage = £77K revenue, correlates with order volume
# STRATEGIC QUESTION: At what order volume does in-house logistics become cheaper?
# WARNING: PAPER CRAFT top revenue inflated by single 80,995 unit order
# that was immediately returned — net revenue for this product = ~£0
# Real top product is likely REGENCY CAKESTAND at £142K
# %%
# Day with the highest consumption
sales["Date"]=sales["InvoiceDate"].dt.weekday
Daily_revenue=sales.groupby("Date")["Revenue"].sum()
print(Daily_revenue)
Daily_revenue.plot(
    figsize=(14,8),
    marker="o",
    color="steelblue"
)
plt.ticklabel_format(style='plain', axis='y')
plt.xticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
plt.title("Daily sale")
plt.ylabel("Total Revenue")
plt.tight_layout()
plt.show()
# INSIGHT: Zero Saturday trading confirms B2B wholesale customer base
# Customers are businesses ordering during business hours
# Thursday have a highest demand -> more product for this day (promotion)
# %%
mask_except_UK=sales["Country"]!="United Kingdom"
country_revenue=sales[mask_except_UK].groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10)
print(country_revenue)
country_revenue.plot(kind="barh",figsize=(14,5),color="steelblue")
plt.title("Top 10 country with highest revenue")
plt.xlabel("Total Revenue")
plt.tight_layout()
plt.show()
# INSIGHT: Netherlands #1 non-UK market — prioritise for expansion
# INSIGHT: EIRE #2 — proximity + shared language = low cost to serve, protect this
# INSIGHT: Australia #5 despite distance — likely British diaspora buying UK gifts
# ACTION: Run targeted promotions for top 5 countries before peak season (Oct-Nov)
# %%
# Finding top customers
# the percentage of revenues assign for specific percent of customers
customer_spend = sales.groupby("CustomerID")["Revenue"].sum().sort_values(ascending=False)
print(customer_spend.describe())

total_customers=len(customer_spend)
top_20_cutoff= int(len(customer_spend) * 0.2)

top_20_revenue=customer_spend.sort_values(ascending=False).iloc[:top_20_cutoff].sum()
total_revenue=customer_spend.sum()

print(f"Total customers:{total_customers:,}")
print(f"Top 20% = {top_20_cutoff} customers")
print(f"Their revenue share:{top_20_revenue/total_revenue:.0%}")

# %%
# find precentage of customer account for certain percentage of revenue
cumulative=customer_spend.cumsum()
total=customer_spend.sum()
customers_needed= (cumulative <= total*0.8).sum()
pct_of_base      = customers_needed / len(customer_spend)
print(f"Customers needed for 80% revenue : {customers_needed:,}")
print(f"As % of total customer base      : {pct_of_base:.1%}")
# 26% of customers (1,132) generate 80% of revenue
# LOSING 100 top cusotmers = LOSING of 1000 bottom ones
# ACTION: GIVING MORE RETENTION MORE DISCOUNTS FOR TOP CUSTOMER
# ACTION: Identify who haven't ordered in last 60 days, contact them immediately
# %%
# Moving onto second data base: return orders
returns=pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\returns.csv", parse_dates=["InvoiceDate"])
returns["ReturnRevenue"]= returns["UnitPrice"]*abs(returns["Quantity"])
print(returns["ReturnRevenue"].describe())
# %%
mask_postage_r=returns["Description"]=="POSTAGE"
mask_manual_r=returns["Description"]=="Manual"
mask_dotcom_r=returns["Description"]=="DOTCOM POSTAGE"
mask_bank_r=returns["Description"]=="Bank Charges"
mask_exclude_r = mask_postage_r | mask_manual_r | mask_dotcom_r | mask_bank_r
returns_clean=returns[mask_exclude==False]
return_by_product=returns_clean.groupby("Description")["ReturnRevenue"].sum()
return_rate= (return_by_product/product_revenue).dropna()
return_rate_clean = return_rate[
    (return_rate <= 1.0) &
    (return_rate > 0)
]
avg_return_rate=return_rate_clean.mean()
# we see somes product have a little impact to actually taken into consideration
# create a filter to see some meaningful impacts and create strategic insights
minimum=100
eligible=product_revenue[product_revenue>minimum].index
return_rate_meaningful=return_rate_clean[return_rate_clean.index.isin(eligible)]
avg_rate = return_rate_meaningful.mean()
print(f"Average return rate (filtered): {avg_return_rate:.1%}")
print(f"\nProducts above 3x average ({avg_return_rate*3:.1%}):")
print(return_rate_meaningful[return_rate_meaningful > avg_return_rate * 3]
      .sort_values(ascending=False).head(10))
# %%
# MEDIUM CERAMIC TOP STORAGE JAR  have the highest return rate so we need to investigate where it is trivial damage or a big one
product = "MEDIUM CERAMIC TOP STORAGE JAR"
sold     = sales[sales["Description"] == product]["Quantity"].sum()
returned = returns[returns["Description"] == product]["Quantity"].abs().sum()
rev      = sales[sales["Description"] == product]["Revenue"].sum()

print(f"Units sold    : {sold}")
print(f"Units returned: {returned}")
print(f"Return rate   : {returned/sold:.1%}")
print(f"Revenue at risk: £{rev:,.2f}")
# INSIGHT: MEDIUM CERAMIC TOP STORAGE JAR — 95.6% return rate
# 74,494 units returned out of 77,916 sold — £81K revenue at risk
# Every unit sold costs: original shipping + return shipping + reprocessing
# Net revenue on this product is likely NEGATIVE after return costs
# ACTION: Immediate supplier quality review + suspend new orders this week
# %%
reference_date=sales["InvoiceDate"].max()+pd.Timedelta(days=1)
rfm=sales.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x:(reference_date-x.max()).days),
    Frequency=("InvoiceNo",  lambda x: x.nunique()),
    Monetary=("Revenue", lambda x: x.sum())
).reset_index()
print(rfm.head(10))
print(rfm.describe())
# %%
print(rfm.loc[rfm["Recency"].idxmax()])
print(rfm.loc[rfm["Frequency"].idxmax()])
print(rfm.loc[rfm["Monetary"].idxmax()])
rfm["R"]=pd.qcut(rfm["Recency"], q=5, labels=[5,4,3,2,1])
rfm["F"]=pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1,2,3,4,5])
rfm["M"]=pd.qcut(rfm["Monetary"], q=5, labels=[1,2,3,4,5])
print(rfm.head(10))
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
rfm["Seg"]=rfm.apply(customer_segment,axis=1)
print(rfm.head(10))
# Later I figured out some customer bought decent amount but for 1 times and quit for long time => not worth chasing they are just testing supplier
# Action: Add another segmentation, the action for those type of cusotmer send one email to ask or advertise not worth investing in long term 
# %%
print(rfm["Seg"].value_counts())
# %%
seg_summary=rfm.groupby("Seg").agg(
    Customers=("CustomerID", "count"),
    Revenue=("Monetary","sum")
).reset_index()
seg_summary["Rev_pct"]=(seg_summary["Revenue"]/seg_summary["Revenue"].sum().round(1))
print(seg_summary.sort_values("Revenue", ascending=False))
# INSIGHT: 962 Champions = 65% of revenue
# INSIGHT: 296 At Risk customers = £687K potentially leaving
# ACTION : Contact At Risk customers before they hit 120 days inactive
# ACTION : Nurture 319 New customers — even converting 10% to Loyal = significant upside
# %%
