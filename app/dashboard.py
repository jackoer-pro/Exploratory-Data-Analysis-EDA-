import streamlit as st
import pandas as pd
import plotly.express as px
# page config
st.set_page_config(
    page_title = "Retail Intelligence",
    page_icon  = "📊",
    layout     = "wide"
)
# load data
@st.cache_data
def load_data():
    path = r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_4\data\processed\\"
    
    sales=pd.read_csv(path + "sales.csv",   parse_dates=["InvoiceDate"])
    returns=pd.read_csv(path+ "returns.csv", parse_dates=["InvoiceDate"])
    rfm=pd.read_csv(path + "segment.csv")

    sales["Revenue"]= sales["Quantity"]*sales["UnitPrice"]
    returns["ReturnRevenue"]= returns["Quantity"].abs()* returns["UnitPrice"]
    
    return sales, returns, rfm
sales,returns,rfm=load_data()
# key numbers
gross_revenue=sales["Revenue"].sum()
return_value=returns["ReturnRevenue"].sum()
net_revenue=gross_revenue-return_value
n_customers=rfm["CustomerID"].nunique()
# Header
st.title("📊 Retail Intelligence Dashboard")
st.caption("UCI Online Retail Dataset · Dec 2010 – Dec 2011")
st.divider()
# key performance indicators
st.subheader("Overview")
c1, c2, c3, c4 = st.columns(4)

c1.metric("Gross Revenue",  f"£{gross_revenue/1e6:.2f}M")
c2.metric("Net Revenue",    f"£{net_revenue/1e6:.2f}M")
c3.metric("Lost to Returns",f"£{return_value/1e3:.0f}K")
c4.metric("Total Customers",f"{n_customers:,}")



