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
## There is not enough data so we assume the pattern stays the same every year, adjusted just by seasonal pattern
avg_monthly=monthly["y"].mean()
monthly["month_num"]=monthly["ds"].dt.month
seasonal_index=monthly.groupby("month_num")["y"].mean()/avg_monthly

print("Seasonal indices:")
print(seasonal_index.round(2))
predict=[12,1,2]
for m in predict:
    predict_revenue=avg_monthly*seasonal_index[m]
    print(f"Month {m}: £{predict_revenue:,.0f}")
# %%
