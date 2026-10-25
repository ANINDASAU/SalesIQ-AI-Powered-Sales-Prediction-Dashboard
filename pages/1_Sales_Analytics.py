import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import monthly_sales, product_sales
from src.dashboard import apply_theme, chart_layout, currency
from src.data_loader import load_sales_data


st.set_page_config(page_title="Sales Analytics | SalesIQ", page_icon="📊", layout="wide")
apply_theme()
st.markdown("<div class='eyebrow'>EXPLORE THE NUMBERS</div>", unsafe_allow_html=True)
st.title("Sales analytics")
st.markdown("<div class='subhead'>Understand how revenue, volume and basket size move together over time.</div>", unsafe_allow_html=True)

try:
	sales, source = load_sales_data()
except Exception as exc:
	st.error(f"Sales data is unavailable: {exc}")
	st.stop()

first, last = sales["InvoiceDate"].min().date(), sales["InvoiceDate"].max().date()
period = st.date_input("Analysis period", (first, last), min_value=first, max_value=last, key="analytics_period")
if not isinstance(period, (tuple, list)) or len(period) != 2:
	st.stop()
data = sales[sales["InvoiceDate"].dt.date.between(*period)].copy()
if data.empty:
	st.info("No records found in this range.")
	st.stop()

monthly = monthly_sales(data)
monthly["Month"] = pd.to_datetime(monthly["Month"])
products = product_sales(data)
metrics = st.columns(3)
metrics[0].metric("Revenue", currency(float(data["Revenue"].sum())))
metrics[1].metric("Transactions", f"{data['InvoiceNo'].nunique():,}")
metrics[2].metric("Avg. selling price", currency(float(data["UnitPrice"].mean())))

left, right = st.columns([1.5, 1], gap="large")
with left:
	st.markdown("#### Revenue and units over time")
	chart_data = monthly.melt("Month", ["Revenue", "Units_Sold"], var_name="Metric", value_name="Value")
	fig = px.line(chart_data, x="Month", y="Value", color="Metric", markers=True, color_discrete_map={"Revenue": "#4f7cff", "Units_Sold": "#19b8a6"})
	fig.update_layout(**chart_layout(), height=390, xaxis_title=None, yaxis_title=None, legend=dict(orientation="h", y=1.13, x=0))
	st.plotly_chart(fig, use_container_width=True)
with right:
	st.markdown("#### Average transaction value")
	monthly_orders = data.assign(Month=data["InvoiceDate"].dt.to_period("M").dt.to_timestamp()).groupby("Month").agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique")).reset_index()
	monthly_orders["Average order"] = monthly_orders["Revenue"] / monthly_orders["Orders"].clip(lower=1)
	fig = px.bar(monthly_orders, x="Month", y="Average order", color_discrete_sequence=["#a48bfa"])
	fig.update_layout(**chart_layout(), height=390, xaxis_title=None, yaxis_title=None)
	st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Product leaderboard")
name_col = "Description" if "Description" in products.columns else "StockCode"
st.dataframe(products.rename(columns={name_col: "Product"}), use_container_width=True, hide_index=True, column_config={"Revenue": st.column_config.NumberColumn(format="$%.2f")})
st.caption(f"Source: {source}. Profit is not available without unit-cost data.")
