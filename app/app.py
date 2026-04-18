import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.data_preprocessing import load_data, preprocess
from src.forecasting import train_model, predict
from src.inventory import calculate_inventory

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Retail Sales Marketing", layout="wide")

# ================= CSS =================
st.markdown("""
<style>

/* Background */
[data-testid="stAppViewContainer"] {
    background-color: #f8fafc;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* KPI Cards */
.kpi {
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    color: white;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.1);
    transition: 0.3s;
}
.kpi:hover {
    transform: translateY(-5px);
}

/* Sections */
.section {
    background: #ffffff;
    padding: 20px;
    border-radius: 14px;
    margin-top: 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.05);
}

/* Titles */
h1, h2, h3 {
    color: #1e293b;
}

</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown("""
<h1 style='text-align:center; 
           font-weight:600; 
           letter-spacing:1px;
           color:#111827;'>
Retail Sales Marketing
</h1>
""", unsafe_allow_html=True)

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
    st.error("No data available for selected filters.")
    st.stop()

if len(filtered_df) < 10:
    st.warning("Not enough data to train model.")
    st.stop()

# ================= MODEL =================
model = train_model(filtered_df)

filtered_df = predict(model, filtered_df)
df = predict(model, df)

# ================= KPI SECTION =================
col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="kpi" style="background: linear-gradient(135deg, #2563eb, #3b82f6);">
    <h3>Total Sales</h3>
    <h2>{int(filtered_df['sales'].sum())}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi" style="background: linear-gradient(135deg, #059669, #10b981);">
    <h3>Total Revenue</h3>
    <h2>₹ {int(filtered_df['revenue'].sum())}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi" style="background: linear-gradient(135deg, #7c3aed, #a78bfa);">
    <h3>Avg Daily Sales</h3>
    <h2>{round(filtered_df['sales'].mean(),2)}</h2>
</div>
""", unsafe_allow_html=True)

# ================= CHART =================
st.markdown('<div class="section"><h3>Sales Trend Analysis</h3></div>', unsafe_allow_html=True)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=filtered_df['date'],
    y=filtered_df['sales'],
    mode='lines',
    name='Actual Sales',
    line=dict(color='#2563eb', width=3),
    fill='tozeroy',
    fillcolor='rgba(37,99,235,0.1)'
))

fig.add_trace(go.Scatter(
    x=filtered_df['date'],
    y=filtered_df['predicted_sales'],
    mode='lines',
    name='Predicted Sales',
    line=dict(color='#7c3aed', width=3, dash='dash')
))

fig.update_layout(
    template='plotly_white',
    height=450,
    margin=dict(l=10, r=10, t=20, b=10),
    xaxis=dict(showgrid=True, gridcolor='#e5e7eb'),
    yaxis=dict(showgrid=True, gridcolor='#e5e7eb'),
    legend=dict(orientation="h", y=1.1)
)

st.plotly_chart(fig, use_container_width=True)

# ================= DATA TABLE =================
st.markdown('<div class="section"><h3>Recent Transactions</h3></div>', unsafe_allow_html=True)
st.dataframe(filtered_df.tail(20), use_container_width=True)

# ================= INVENTORY =================
st.markdown('<div class="section"><h3>Inventory Insights</h3></div>', unsafe_allow_html=True)

inventory = calculate_inventory(df)
inv_df = pd.DataFrame(inventory)

st.dataframe(inv_df, use_container_width=True)

# ================= ALERT =================
low = inv_df[inv_df['status']=="Low Demand"]

if not low.empty:
    st.markdown("""
    <div style="background:#fee2e2;color:#7f1d1d;padding:15px;border-radius:10px;">
    Inventory Alert: Some products show low demand. Adjust stock levels.
    </div>
    """, unsafe_allow_html=True)