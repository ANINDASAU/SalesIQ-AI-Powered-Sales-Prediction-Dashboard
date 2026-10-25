import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import calculate_kpis, monthly_sales, product_sales
from src.data_loader import load_sales_data
from src.dashboard import apply_theme, chart_layout, currency


st.set_page_config(
    page_title="SalesIQ | Executive overview",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

try:
    sales, source = load_sales_data()
except Exception as exc:
    st.error("Sales data could not be loaded. Check the database configuration or Excel fallback.")
    st.caption(str(exc))
    st.stop()

if sales.empty:
    st.warning("No valid sales were found. Add sales to MySQL or the source workbook.")
    st.stop()

minimum_date = sales["InvoiceDate"].min().date()
maximum_date = sales["InvoiceDate"].max().date()
with st.sidebar:
    st.markdown("<div class='brand-mark'>◈ <span>SalesIQ</span></div>", unsafe_allow_html=True)
    st.caption("INTELLIGENCE • OVERVIEW")
    st.divider()
    selected_range = st.date_input(
        "Reporting period",
        value=(minimum_date, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
        key="overview_reporting_period",
        help="Select the date range to include in the dashboard.",
    )
    all_products = sorted(sales["Description"].dropna().astype(str).unique())
    selected_products = st.multiselect("Products", all_products, placeholder="All products", key="overview_products")
    all_countries = sorted(sales["Country"].dropna().astype(str).unique())
    selected_countries = st.multiselect("Markets", all_countries, placeholder="All markets", key="overview_markets")
    st.divider()
    st.caption(f"Data source · {source}")
    if st.button("↻  Refresh data", use_container_width=True, key="overview_refresh_data"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Data refreshes automatically every 5 minutes")

if not isinstance(selected_range, (tuple, list)) or len(selected_range) != 2:
    st.info("Choose both a start and end date in the sidebar.")
    st.stop()
import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import calculate_kpis, monthly_sales, product_sales
from src.data_loader import load_sales_data
from src.dashboard import apply_theme, chart_layout, currency


st.set_page_config(
    page_title="SalesIQ | Executive overview",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

try:
    sales, source = load_sales_data()
except Exception as exc:
    st.error("Sales data could not be loaded. Check the database configuration or Excel fallback.")
    st.caption(str(exc))
    st.stop()

if sales.empty:
    st.warning("No valid sales were found. Add sales to MySQL or the source workbook.")
    st.stop()

minimum_date = sales["InvoiceDate"].min().date()
maximum_date = sales["InvoiceDate"].max().date()
with st.sidebar:
    st.markdown("<div class='brand-mark'>◈ <span>SalesIQ</span></div>", unsafe_allow_html=True)
    st.caption("INTELLIGENCE • OVERVIEW")
    st.divider()
    selected_range = st.date_input(
        "Reporting period",
        value=(minimum_date, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
        help="Select the date range to include in the dashboard.",
    )
    all_products = sorted(sales["Description"].dropna().astype(str).unique())
    selected_products = st.multiselect("Products", all_products, placeholder="All products")
    all_countries = sorted(sales["Country"].dropna().astype(str).unique())
    selected_countries = st.multiselect("Markets", all_countries, placeholder="All markets")
    st.divider()
    st.caption(f"Data source · {source}")
    st.caption("Refreshes automatically every 5 minutes")

if not isinstance(selected_range, (tuple, list)) or len(selected_range) != 2:
    st.info("Choose both a start and end date in the sidebar.")
    st.stop()
start_date, end_date = selected_range
if start_date > end_date:
    st.error("The start date must not be after the end date.")
    st.stop()

filtered = sales[sales["InvoiceDate"].dt.date.between(start_date, end_date)].copy()
if selected_products:
    filtered = filtered[filtered["Description"].astype(str).isin(selected_products)]
if selected_countries:
    filtered = filtered[filtered["Country"].astype(str).isin(selected_countries)]

st.markdown("<div class='eyebrow'>BUSINESS PERFORMANCE</div>", unsafe_allow_html=True)
st.title("Sales at a glance")
st.markdown(
    f"<div class='subhead'>A clear view of revenue, customer demand and product momentum. &nbsp;·&nbsp; {start_date:%b %d, %Y} — {end_date:%b %d, %Y}</div>",
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No sales match these filters. Try a wider date range or clear a filter.")
    st.stop()

kpis = calculate_kpis(filtered)
monthly = monthly_sales(filtered)
products = product_sales(filtered)
prior_period_start = start_date - (end_date - start_date + pd.Timedelta(days=1))
prior = sales[
    sales["InvoiceDate"].dt.date.between(prior_period_start, start_date - pd.Timedelta(days=1))
]
if selected_products:
    prior = prior[prior["Description"].astype(str).isin(selected_products)]
if selected_countries:
    prior = prior[prior["Country"].astype(str).isin(selected_countries)]
prior_revenue = float(prior["Revenue"].sum())
growth = ((kpis["revenue"] - prior_revenue) / prior_revenue * 100) if prior_revenue else None
growth_label = f"{growth:+.1f}% vs previous period" if growth is not None else "No prior-period baseline"

cards = st.columns(4)
cards[0].metric("Net sales", currency(kpis["revenue"]), growth_label)
cards[1].metric("Orders", f"{kpis['orders']:,}", "Unique invoices")
cards[2].metric("Units sold", f"{kpis['units_sold']:,}", f"{products['StockCode'].nunique():,} products")
cards[3].metric("Average order", currency(kpis["average_order_value"]), "Revenue per invoice")

left, right = st.columns([1.65, 1], gap="large")
with left:
    st.markdown("#### Revenue trajectory")
    trend = monthly.copy()
    trend["Month"] = pd.to_datetime(trend["Month"])
    fig = px.area(trend, x="Month", y="Revenue", color_discrete_sequence=["#4f7cff"])
    fig.update_traces(line=dict(width=2.8), fillcolor="rgba(79,124,255,0.13)", hovertemplate="%{x|%b %Y}<br>Revenue: %{y:,.2f}<extra></extra>")
    fig.update_layout(**chart_layout(), height=345, xaxis_title=None, yaxis_title=None, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Revenue by month")
    fig = px.bar(trend, x="Month", y="Revenue", color_discrete_sequence=["#19b8a6"])
    fig.update_traces(hovertemplate="%{x|%b %Y}<br>Revenue: %{y:,.2f}<extra></extra>")
    fig.update_layout(**chart_layout(), height=345, xaxis_title=None, yaxis_title=None, bargap=0.35)
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns([1.15, 1], gap="large")
with left:
    st.markdown("#### Best-selling products")
    top_products = products.head(8).sort_values("Revenue")
    label = "Description" if "Description" in top_products.columns else "StockCode"
    fig = px.bar(top_products, x="Revenue", y=label, orientation="h", color="Revenue", color_continuous_scale=["#a6baff", "#4f7cff"])
    fig.update_layout(**chart_layout(), height=335, xaxis_title=None, yaxis_title=None, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Revenue by market")
    markets = filtered.groupby("Country", as_index=False).agg(Revenue=("Revenue", "sum")).nlargest(8, "Revenue")
    fig = px.pie(markets, names="Country", values="Revenue", hole=0.66, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition="inside", textinfo="percent", hovertemplate="%{label}<br>Revenue: %{value:,.2f}<extra></extra>")
    fig.update_layout(**chart_layout(), height=335, legend=dict(orientation="h", y=-0.12, x=0))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Sales detail")
show_columns = ["InvoiceDate", "InvoiceNo", "Description", "Country", "Quantity", "UnitPrice", "Revenue"]
st.dataframe(
    filtered[show_columns].sort_values("InvoiceDate", ascending=False).head(1_000),
    use_container_width=True,
    hide_index=True,
    height=320,
    column_config={
        "InvoiceDate": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
        "Revenue": st.column_config.NumberColumn("Revenue", format="$%0.2f"),
        "UnitPrice": st.column_config.NumberColumn("Unit price", format="$%0.2f"),
    },
)
if len(filtered) > 1_000:
    st.caption(f"Showing the latest 1,000 of {len(filtered):,} matching rows. Export includes all matching transactions.")
st.download_button("↓  Export filtered sales", filtered[show_columns].to_csv(index=False).encode("utf-8"), "salesiq_filtered_sales.csv", "text/csv")
st.caption("Profit is not estimated because product cost data is not present in the current source dataset.")