#%%
import pandas as pd
sales = pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\sales.csv", parse_dates=["InvoiceDate"])
sales["Revenue"]=sales["Quantity"]*sales["UnitPrice"]
sales["Month"]=sales["InvoiceDate"].dt.to_period("M")
monthly=sales.groupby("Month")["Revenue"].sum().reset_index()
# rename it like x and y so the model can learn
monthly.columns=["ds","y"]
monthly["ds"]=monthly["ds"].dt.to_timestamp()
monthly=monthly[:-1]
print(monthly)
print(f"\nRows: {len(monthly)}")
print(f"Date range: {monthly['ds'].min()} → {monthly['ds'].max()}")
# %%
# verify that the amount of data is not enough to create powerful predictions
from prophet import Prophet
model=Prophet(
    growth = "flat",
    yearly_seasonality=True,
    weekly_seasonality=False,
    uncertainty_samples=1000,
    interval_width=0.80,
    daily_seasonality=False
)
model.fit(monthly)
print("Model fitted successfully.")
# show what the model suppose to d
future=model.make_future_dataframe(periods=3, freq="MS")
print(future)
# show the lowest prediction and highest the range of it (with confidence around 80%)
forecast = model.predict(future)
print(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(6))
# %%
