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
net_revenue=(gross_revenue-return_value)
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
    # Top 10 country
    st.subheader("Top 10 countries (ex UK)")
    mask_ex_uk= sales["Country"]!="United Kingdom"
    country_revenue=sales[mask_ex_uk].groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10).reset_index()
    fig=px.bar(country_revenue, x="Revenue", y="Country", orientation="h" ,color_discrete_sequence=["blue"])
    fig.update_layout(xaxis_tickprefix="£", height=400)
    st.plotly_chart(fig, use_container_width=True)
# build 2 bar chart side by side indicates customer and revenue percentage per segment
elif page=="Customer Segments":
    seg_summary=rfm.groupby("Seg").agg(
        Customers= ("CustomerID", "count"),    
        Revenue=("Monetary", "sum")           
    ).reset_index()
    seg_summary["Rev_pct"]=(seg_summary["Revenue"]/seg_summary["Revenue"].sum()*100).round(1)
    col1,col2=st.columns(2)
    with col1:
        st.subheader("Customers per Segment")
        fig1=px.bar(seg_summary.sort_values("Customers"), x="Seg",y="Customers",color_discrete_sequence=["steelblue"] )
        st.plotly_chart(fig1, use_container_width=True, key="customers_chart")
    with col2:
        st.subheader("Revenue % per Segment")
        fig2=px.bar(seg_summary, x="Seg",y="Rev_pct",color_discrete_sequence=["orange"], labels={"Rev_pct": "Revenue % per Segment "} )
        st.plotly_chart(fig2, use_container_width=True, key="revenue_chart")
    # scateter plot between recency and moentary
    st.subheader("Recency and Monetary")
    fig3 = px.scatter(rfm, x="Recency", y="Monetary", 
                  color="Seg", opacity=0.5,
                  hover_data=["CustomerID", "Frequency"],
                  labels={"Recency": "Days since last purchase",
                          "Monetary": "Total spend (£)"})
    st.plotly_chart(fig3, use_container_width=True, key="scatter_chart")
    # customer table
    st.subheader("Customer Table")
    selected = st.multiselect("Filter by segment", 
                           options=rfm["Seg"].unique(),
                           default=["Champion", "At risk"])
    filtered = rfm[rfm["Seg"].isin(selected)]
    st.dataframe(filtered, use_container_width=True)
elif page == "Product Analysis":
    mask_postage=sales["Description"]=="POSTAGE"
    mask_manual=sales["Description"]=="Manual"
    mask_dotcom=sales["Description"]=="DOTCOM POSTAGE"
    mask_exclude = mask_postage | mask_manual | mask_dotcom
    sales_product=sales[mask_exclude==False]
    product_revenue=sales_product.groupby("Description")["Revenue"].sum()
    top_15_revenue=product_revenue.sort_values(ascending=False).head(15)
    top_15_df = top_15_revenue.reset_index()

    mask_postage_r=returns["Description"]=="POSTAGE"
    mask_manual_r=returns["Description"]=="Manual"
    mask_dotcom_r=returns["Description"]=="DOTCOM POSTAGE"
    mask_bank_r=returns["Description"]=="Bank Charges"
    mask_exclude_r = mask_postage_r | mask_manual_r | mask_dotcom_r | mask_bank_r
    returns_clean=returns[mask_exclude_r==False]
    return_by_product=returns_clean.groupby("Description")["ReturnRevenue"].sum()

    return_rate= (return_by_product/product_revenue).dropna()
    min_sales = 100
    eligible = product_revenue[product_revenue >= min_sales].index

    return_rate_clean = return_rate[
    (return_rate <= 1.0) &
    (return_rate > 0) &
    (return_rate.index.isin(eligible))
    ]

    st.subheader("Top 15 products by revenue")
    fig5=px.bar(top_15_df.sort_values("Revenue"), x="Revenue", y="Description", orientation="h" ,color_discrete_sequence=["blue"])
    fig5.update_layout(xaxis_tickprefix="£", height=400)
    st.plotly_chart(fig5, use_container_width=True)
    st.subheader("Highest return rate products")
    return_rate_df = return_rate_clean.reset_index()
    return_rate_df.columns = ["Description", "ReturnRate"]
    return_rate_df["ReturnRate"] = (return_rate_df["ReturnRate"] * 100).round(1)

    fig6 = px.bar(return_rate_df.sort_values("ReturnRate").tail(10),
              x="ReturnRate", y="Description", orientation="h",
              color_discrete_sequence=["coral"])
    fig6.update_layout(xaxis_ticksuffix="%", height=500)
    st.plotly_chart(fig6, use_container_width=True)
    

