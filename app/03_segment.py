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