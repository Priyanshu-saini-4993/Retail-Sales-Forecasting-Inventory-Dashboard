import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd

from src.data_preprocessing import load_data, preprocess
from src.forecasting import train_model, predict
from src.inventory import calculate_inventory

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")

# ================= CUSTOM CSS =================
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}

.kpi-card {
    padding: 20px;
    border-radius: 12px;
    color: white;
    font-weight: bold;
    text-align: center;
}

.kpi-sales { background: linear-gradient(135deg, #667eea, #764ba2); }
.kpi-revenue { background: linear-gradient(135deg, #43cea2, #185a9d); }
.kpi-avg { background: linear-gradient(135deg, #ff9966, #ff5e62); }

.section {
    padding: 10px;
    border-left: 5px solid #4CAF50;
    background-color: #ffffff;
    margin-top: 20px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown("<h1 style='text-align:center;'>Retail Sales Forecasting & Inventory Dashboard</h1>", unsafe_allow_html=True)

# ================= LOAD DATA =================
df = load_data("data/sales_data.csv")
df = preprocess(df)

# ================= SIDEBAR =================
st.sidebar.title("Filters")

category = st.sidebar.selectbox("Category", sorted(df['category'].unique()))
filtered_category = df[df['category'] == category]

product = st.sidebar.selectbox("Product", sorted(filtered_category['product'].unique()))
filtered_product = filtered_category[filtered_category['product'] == product]

store = st.sidebar.selectbox("Store", sorted(filtered_product['store'].unique()))
filtered_df = filtered_product[filtered_product['store'] == store]

# ================= SAFETY =================
if filtered_df.empty:
    st.error("No data available")
    st.stop()

if len(filtered_df) < 10:
    st.warning("Not enough data")
    st.stop()

# ================= MODEL =================
model = train_model(filtered_df)
filtered_df = predict(model, filtered_df)
df = predict(model, df)

# ================= KPI CARDS =================
col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="kpi-card kpi-sales">
    <h3>Total Sales</h3>
    <h2>{int(filtered_df['sales'].sum())}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card kpi-revenue">
    <h3>Total Revenue</h3>
    <h2>₹ {int(filtered_df['revenue'].sum())}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card kpi-avg">
    <h3>Avg Daily Sales</h3>
    <h2>{round(filtered_df['sales'].mean(),2)}</h2>
</div>
""", unsafe_allow_html=True)

# ================= SALES CHART =================
st.markdown('<div class="section"><h3>Sales Trend</h3></div>', unsafe_allow_html=True)

chart = filtered_df.set_index("date")[["sales","predicted_sales"]]
import plotly.graph_objects as go

st.markdown('<div class="section"><h3>Sales Trend Analysis</h3></div>', unsafe_allow_html=True)

fig = go.Figure()

# Actual Sales
fig.add_trace(go.Scatter(
    x=filtered_df['date'],
    y=filtered_df['sales'],
    mode='lines',
    name='Actual Sales',
    line=dict(color='#4CAF50', width=3)
))

# Predicted Sales
fig.add_trace(go.Scatter(
    x=filtered_df['date'],
    y=filtered_df['predicted_sales'],
    mode='lines',
    name='Predicted Sales',
    line=dict(color='#FF5733', width=3, dash='dash')
))

# Layout styling
fig.update_layout(
    template='plotly_white',
    height=450,
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        orientation="h",
        y=1.1,
        x=0.3
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor='lightgray'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='lightgray'
    ),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ================= DATA TABLE =================
st.markdown('<div class="section"><h3>Recent Transactions</h3></div>', unsafe_allow_html=True)
st.dataframe(filtered_df.tail(20), use_container_width=True)

# ================= INVENTORY =================
st.markdown('<div class="section"><h3>Inventory Recommendations</h3></div>', unsafe_allow_html=True)

inventory = calculate_inventory(df)
inv_df = pd.DataFrame(inventory)

# Highlight low demand
def highlight(row):
    if row['status'] == 'Low Demand':
        return ['background-color: #ffcccc'] * len(row)
    elif row['status'] == 'High Demand':
        return ['background-color: #ccffcc'] * len(row)
    return [''] * len(row)

st.dataframe(inv_df.style.apply(highlight, axis=1), use_container_width=True)

# ================= ALERT =================
low = inv_df[inv_df['status']=="Low Demand"]

if not low.empty:
    st.markdown("""
    <div style="background-color:#ffe6e6;padding:10px;border-radius:8px;">
    <b>Alert:</b> Some products show low demand. Consider reducing inventory.
    </div>
    """, unsafe_allow_html=True)