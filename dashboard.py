import streamlit as st
import plotly.express as px 
import pandas as pd 
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title = "Cafe Sales", page_icon = ":bar_chart:", layout = "wide")

st.title(":bar_chart: Cafe Sales EDA")
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
item  = st.sidebar.multiselect("Choose Item", df["Item"].unique())
if not item: 
    df2 = df.copy()
else: 
    df2 = df[df["Item"].isin(item)]

#Create for location 
location  = st.sidebar.multiselect("Choose Location", df["Location"].unique())
if not location: 
    df3 = df2.copy()
else: 
    df3 = df2[df2["Location"].isin(location)]
