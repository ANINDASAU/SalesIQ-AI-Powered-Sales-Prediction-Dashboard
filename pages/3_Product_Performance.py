import plotly.express as px
import streamlit as st

from src.analytics import product_sales
from src.dashboard import apply_theme, chart_layout, currency
from src.data_loader import load_sales_data


st.set_page_config(page_title="Product Performance | SalesIQ", page_icon="📦", layout="wide")
apply_theme()
st.markdown("<div class='eyebrow'>PORTFOLIO HEALTH</div>", unsafe_allow_html=True)
st.title("Product performance")
st.markdown("<div class='subhead'>Find the products driving sales and discover where demand is concentrated.</div>", unsafe_allow_html=True)

try:
	sales, source = load_sales_data()
except Exception as exc:
	st.error(f"Sales data is unavailable: {exc}")
	st.stop()

product_table = product_sales(sales)
if product_table.empty:
	st.info("No product sales are available yet.")
	st.stop()

name_column = "Description" if "Description" in product_table.columns else "StockCode"
choice = st.selectbox("Focus product", ["All products"] + product_table[name_column].fillna("Unknown").astype(str).tolist())
if choice != "All products":
	sales = sales[sales["Description"].astype(str).eq(choice)]
	product_table = product_sales(sales)

top = product_table.iloc[0]
cards = st.columns(4)
cards[0].metric("Products", f"{product_table['StockCode'].nunique():,}")
cards[1].metric("Portfolio revenue", currency(float(product_table["Revenue"].sum())))
cards[2].metric("Top product", str(top.get(name_column, top["StockCode"]))[:24])
cards[3].metric("Top product share", f"{float(top['Revenue']) / max(float(product_table['Revenue'].sum()), 1) * 100:.1f}%")

left, right = st.columns([1.5, 1], gap="large")
with left:
	st.markdown("#### Revenue leaders")
	chart_data = product_table.head(12).sort_values("Revenue")
	fig = px.bar(chart_data, x="Revenue", y=name_column, orientation="h", color="Revenue", color_continuous_scale=["#b8c7ff", "#4f7cff"])
	fig.update_layout(**chart_layout(), height=460, xaxis_title=None, yaxis_title=None, coloraxis_showscale=False)
	st.plotly_chart(fig, use_container_width=True)
with right:
	st.markdown("#### Revenue vs. units")
	fig = px.scatter(product_table, x="Units_Sold", y="Revenue", size="Orders", color="Revenue", hover_name=name_column, color_continuous_scale="Tealgrn", size_max=35)
	fig.update_layout(**chart_layout(), height=460, xaxis_title="Units sold", yaxis_title="Revenue", coloraxis_showscale=False)
	st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Full product catalog")
st.dataframe(product_table, use_container_width=True, hide_index=True, column_config={"Revenue": st.column_config.NumberColumn(format="$%.2f")})
st.download_button("↓  Export product report", product_table.to_csv(index=False).encode("utf-8"), "salesiq_product_performance.csv", "text/csv")
st.caption(f"Source: {source}. Rankings use transaction revenue; profit/margin requires unit-cost data.")
