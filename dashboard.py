import streamlit as st
import plotly.express as px 
import plotly.graph_objects as go
import pandas as pd 
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title = "Cafe Sales", page_icon = ":bar_chart:", layout = "wide")

st.title(":bar_chart: Cafe Sales Interactive Dashboard")
st.markdown('<style>.div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

fl= st.file_uploader("Upload a file", type= (["csv", "txt", "xlsx", "xls"]))
if fl is not None: 
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else: 
    os.chdir(r"/Users/vullnetvoca/Desktop/Cafe Sales Data Cleaning")
    df = pd.read_csv("sales_cleaned.csv", encoding = "ISO-8859-1")


col1, col2 = st.columns ((2))

df["Transaction Date"] = pd.to_datetime(df["Transaction Date"])

startDate = df["Transaction Date"].min()
endDate = df["Transaction Date"].max()

with col1: 
    date1 = st.date_input("Start Date", startDate)

with col2:
    date2 = st.date_input("End Date", endDate)

start = pd.to_datetime(date1)
end = pd.to_datetime(date2)
                          
df = df[
    (df["Transaction Date"] >= start) & 
    (df["Transaction Date"] <= end)].copy() 

st.sidebar.header("Choose your filter:")

#Create for item
payment  = st.sidebar.multiselect("Choose Payment Method", df["Payment Method"].unique())
if not payment: 
    df2 = df.copy()
else: 
    df2 = df[df["Payment Method"].isin(payment)]

#Create for location 
location  = st.sidebar.multiselect("Choose Location", df["Location"].unique())
if not location: 
    df3 = df2.copy()
else: 
    df3 = df2[df2["Location"].isin(location)]

#Filter data based on item and location 
if not payment and not location: 
    filter_df = df 
elif not location: 
    filter_df = df[df["Payment Method"].isin(payment)]
elif not payment:
    filter_df = df[df["Location"].isin(location)]
else:
    filter_df = df[
        (df["Payment Method"].isin(payment)) &
        (df["Location"].isin(location))
        ]

#Main KPI on top 
total_revenue = filter_df["Total Spent"].sum()
total_items = filter_df["Quantity"].sum()

kpi1, kpi2 = st.columns(2)

kpi1.metric("Total Revenue", f"£{total_revenue:,.2f}")
kpi2.metric("Items Sold", total_items)

#Total Sales and Revenue by Item
revenue_item = filter_df.groupby( by = ["Item"], as_index = False)["Total Spent"].sum()
sales_item = filter_df.groupby( by = ["Item"], as_index = False)["Quantity"].sum()

with col1: 
    st.subheader("Revenue by Item")
    fig = px.bar(revenue_item, x= "Item", y = "Total Spent", text = ["£".format(x) for x in revenue_item["Total Spent"]], 
                 color="Total Spent", color_continuous_scale="Blues", template="seaborn")
    st.plotly_chart(fig, use_container_width= True, height = 200)

with col2: 
    st.subheader("Sales Volume by Item")
    fig = px.bar(sales_item, x= "Item", y = "Quantity",
                 color="Quantity", color_continuous_scale="Oranges",template="seaborn")
    st.plotly_chart(fig, use_container_width= True, height = 200)


cl1, cl2 = st.columns(2)

with cl1: 
    with st.expander("View Sales Revenue Data"):
        st.write(revenue_item.style.background_gradient(cmap="Blues"))
        csv = revenue_item.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data", data = csv, file_name = "ItemRevenue.csv", mime = "text/csv",
                           help = "Click here to download the data as a CSV file.")
        
with cl2: 
    with st.expander("View Sales Volume Data"):
        st.write(sales_item.style.background_gradient(cmap="Oranges"))
        csv = sales_item.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data", data = csv, file_name = "ItemVolume.csv", mime = "text/csv",
                           help = "Click here to download the data as a CSV file.")
        


st.subheader("Time Series Analysis")

#Get daily sales and 7-day and 30-day rolling averages

Daily_Sales = filter_df.groupby("Transaction Date")["Total Spent"].sum().sort_index()
rolling_7 = Daily_Sales.rolling(window=7).mean()
rolling_30 = Daily_Sales.rolling(window=30).mean()

accel = rolling_7.diff()
z = (accel - accel.mean()) / accel.std()
spikes = z[abs(z) > 2]

fig2 = px.line(x=Daily_Sales.index, y=Daily_Sales.values, title = "Daily Sales")
st.plotly_chart(fig2,use_container_width=True)


fig3=go.Figure()
#7 day rolling average
fig3.add_trace(go.Scatter(x=rolling_7.index, y=rolling_7.values, mode = "lines", name="7 Day Average"))
#spike in 7 day rolling average
fig3.add_trace(go.Scatter(x=spikes.index, y=rolling_7.loc[spikes.index], mode="markers", name="Sudden Change", marker=dict(size=8, color="orange")))
#30 day average 
fig3.add_trace(go.Scatter(x=rolling_30.index, y=rolling_30.values, mode = "lines", name="30 Day Average"))
fig3.update_layout(title="Sales Trends with Rolling Averages", xaxis_title = "Date", yaxis_title="Revenue")
st.plotly_chart(fig3,use_container_width=True)


pie1, pie2 = st.columns(2)

#Total Revnue by Payment Method and Location
revenue_pay = filter_df.groupby(by = ["Payment Method"], as_index = False)["Total Spent"].sum()
revenue_loc = filter_df.groupby(by = ["Location"], as_index = False)["Total Spent"].sum()

with pie1: 
    st.subheader("Revenue by Payment Method")
    fig4 = px.pie(revenue_pay, names= "Payment Method", values = "Total Spent", template="seaborn")
    st.plotly_chart(fig4, use_container_width= True, height = 200)

with pie2: 
    st.subheader("Revenue by Location")
    fig5 = px.pie(revenue_loc, names = "Location", values = "Total Spent",template="seaborn")
    st.plotly_chart(fig5, use_container_width= True, height = 200)