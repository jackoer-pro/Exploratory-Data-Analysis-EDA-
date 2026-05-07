
# get the overal picture about the data
# %%
import pandas as pd
df_raw = pd.read_excel(
    r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\Online Retail.xlsx",
    dtype={"CustomerID": str}
)
#%%
print(df_raw.shape)
print(df_raw.head(10))
print(df_raw.dtypes)
print(df_raw.isnull().sum())
print(df_raw["Quantity"].max())
print(df_raw["Quantity"].min())
print(df_raw["UnitPrice"].max())
print(df_raw["UnitPrice"].min())
#%%
#how many return order
mask_returns= df_raw["InvoiceNo"].str.startswith("C")
print("Return order:",mask_returns.sum())
# how many row have no customer(id) (internal adjustment/loss)
mask_no_cus=df_raw["CustomerID"].isnull()
print("No customer:",mask_no_cus.sum())
# how many rows have negative quatity (return or loss)
mask_qty_neg=df_raw["Quantity"] < 0
print("Negative qty:", mask_qty_neg.sum())
# how many row have zero unit price (internal adjustment)
mask_zero=df_raw["UnitPrice"]==0
print("Zero price:", mask_zero.sum())
# how many row have negative unit price ( write off debt)
mask_neg_price=df_raw["UnitPrice"]<0
print("Negative price:", mask_neg_price.sum())
# %%
is_return = df_raw["InvoiceNo"].astype(str).str.startswith("C")
# Rows that have no customer and negative quantity (internal loss)
# first type
mask_damage = (
    (df_raw["CustomerID"].isnull()) &
    (df_raw["Quantity"] < 0) &
    (df_raw["UnitPrice"] == 0)
)
print("Damage write-off:", mask_damage.sum())

# Rows that have no cusotmer and zero price (internal adjustment)
# stock correction without damange
# second type
mask_stock_correction = (df_raw["CustomerID"].isnull()) & ((df_raw["UnitPrice"]==0)) & (df_raw["Quantity"]>0)
print("Stock corrections:", mask_stock_correction.sum())
# Rows that are normal sale
# third type
mask_normal_sale =  ((is_return == False) & 
                    (df_raw["CustomerID"].notna()) &
                    (df_raw["UnitPrice"]>0)&
                    (df_raw["Quantity"]>0)
                )
print("Normal sales:", mask_normal_sale.sum())
# fourth type
# return order
mask_returns= df_raw["InvoiceNo"].str.startswith("C")
print("Return order:",mask_returns.sum())
# fifth type
# Bad-debt write off
mask_debt= df_raw["UnitPrice"]<0
print("Bad debt write off:", mask_debt.sum())
# sixth type 
# promotion/sample for customer
no_customer_involved=df_raw["CustomerID"].isnull()
mask_trial= ((df_raw["Quantity"]>0) &
             (no_customer_involved==False) &
             (df_raw["UnitPrice"]==0)
             )
print("Sample/Promotion:", mask_trial.sum())
# seventh type
# Unlinked transactions — no CustomerID but real value
# Mix of: postage fee entries, manual/wholesale orders
# Exclude from customer analysis. Include in gross revenue with caution.
mask_anon_sale=((df_raw["Quantity"]>0)&
                   (df_raw["UnitPrice"]>0)&
                   (df_raw["CustomerID"].isnull())
                    )
print("Anonymous sales:",mask_anon_sale.sum())
total= mask_damage.sum()+mask_stock_correction.sum()+mask_normal_sale.sum()+mask_returns.sum()+mask_debt.sum()+mask_trial.sum()+mask_anon_sale.sum()
print("Total sale=", total)
print(df_raw.shape)
# %%
# some conditions are overlaped and appear multiple time so I need to figure it out
overlap = (mask_returns) & (mask_damage)
print("Overlap between returns and internal loss:", overlap.sum())
print(df_raw[overlap][['InvoiceNo','CustomerID','Quantity','UnitPrice']].head())

# %%
print(df_raw[mask_anon_sale][['InvoiceNo','Description','Quantity','UnitPrice','CustomerID']].head(20))
# to find out why some transations have some pattern with normal sale without customer ID
# %%
anon = df_raw[mask_anon_sale]
print(anon['Quantity'].describe())
print(anon['UnitPrice'].describe())
print(anon['Description'].value_counts().head(10))
# by doing so we be able to detect that transaction is from postal fee, manual/ wholesome order
# %%
df_raw[mask_normal_sale].to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\sales.csv",index=False)
df_raw[mask_stock_correction].to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\stock_corrections.csv",index=False)
df_raw[mask_damage].to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\damage.csv",index=False)
df_raw[is_return].to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\returns.csv",index=False)
df_raw[mask_trial].to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\samples.csv",index=False)
df_raw[mask_debt].to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\bad_debt.csv",index=False)
df_raw[mask_anon_sale].to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\anonymous.csv",index=False)
print("saved sucessfully")
# %%
sales = pd.read_excel(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\sales.csv", parse_dates=["InvoiceDate"])
sales["Revenue"]=sales["Quantity"]*sales["UnitPrice"]
