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
# side bar
st.divider()
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Revenue & Time", "Customer Segments", "Product Analysis"]
)
if page== "Revenue & Time":
    # monthly trend
    st.subheader("Revenue over time")
    sales["Month"]=sales["InvoiceDate"].dt.to_period("M").astype(str)
    monthly=sales.groupby("Month")["Revenue"].sum().reset_index()

    fig= px.line(monthly, x="Month", y="Revenue",
                 markers=True,
                 color_discrete_sequence=["steelblue"])
    fig.update_layout(yaxis_tickprefix="£", height=400)
    st.plotly_chart(fig, use_container_width=True)
    # Daily trend
    st.subheader("Daily revenue trend")
    sales["Day"]=sales["InvoiceDate"].dt.day_name()
    daily=sales.groupby("Day")["Revenue"].sum().reset_index()
    day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
    ]

    daily["Day"] = pd.Categorical(
        daily["Day"],
        categories=day_order,
     ordered=True
    )

    daily = daily.sort_values("Day")
    
    fig=px.bar(daily, x="Revenue", y="Day", orientation="h", color_discrete_sequence=["orange"])
    fig.update_layout(xaxis_tickprefix="£", height=400)
    st.plotly_chart(fig, use_container_width=True )


