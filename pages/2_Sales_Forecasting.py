import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analytics import monthly_sales
from src.dashboard import apply_theme, chart_layout, currency
from src.data_loader import load_sales_data
from src.predict import forecast_sales


st.set_page_config(page_title="Sales Forecast | SalesIQ", page_icon="🔮", layout="wide")
apply_theme()
st.markdown("<div class='eyebrow'>PLAN WITH CONFIDENCE</div>", unsafe_allow_html=True)
st.title("Sales forecast")
st.markdown("<div class='subhead'>A machine-learning view of likely revenue ahead, built from your monthly sales history.</div>", unsafe_allow_html=True)

try:
	sales, source = load_sales_data()
except Exception as exc:
	st.error(f"Sales data is unavailable: {exc}")
	st.stop()

monthly = monthly_sales(sales)
if len(monthly) < 4:
	st.warning("At least four months of data are needed before forecasting.")
	st.stop()

controls = st.columns([1, 3])
horizon = controls[0].select_slider("Forecast horizon", options=[3, 6, 9, 12], value=6, format_func=lambda months: f"{months} months")
controls[1].markdown(f"<div style='padding-top:2rem;color:#77839a'>History: {len(monthly)} months &nbsp;·&nbsp; Source: {source}</div>", unsafe_allow_html=True)
try:
	forecast, metrics = forecast_sales(monthly, horizon)
except ValueError as exc:
	st.warning(str(exc))
	st.stop()

latest_actual = float(monthly.iloc[-1]["Revenue"])
forecast_total = float(forecast["Revenue"].sum())
cards = st.columns(3)
cards[0].metric("Forecast next month", currency(float(forecast.iloc[0]["Revenue"])), f"{(float(forecast.iloc[0]['Revenue']) / latest_actual - 1) * 100:+.1f}% vs latest month" if latest_actual else None)
cards[1].metric(f"Projected {horizon}-month revenue", currency(forecast_total))
if pd.notna(metrics["mae"]):
	cards[2].metric("Holdout MAE", currency(float(metrics["mae"])), "Lower is better")
else:
	cards[2].metric("Forecast approach", "Trend baseline", "More history improves model quality")

st.markdown("#### Actuals and projection")
historical = monthly.copy()
historical["Month"] = pd.to_datetime(historical["Month"])
cutoff = historical["Month"].max()
fig = go.Figure()
fig.add_trace(go.Scatter(x=historical["Month"], y=historical["Revenue"], mode="lines+markers", name="Actual revenue", line=dict(color="#4f7cff", width=3), fill="tozeroy", fillcolor="rgba(79,124,255,.10)"))
bridge_x = pd.concat([pd.Series([cutoff]), forecast["Month"]], ignore_index=True)
bridge_y = pd.concat([pd.Series([float(historical.iloc[-1]["Revenue"])]), forecast["Revenue"]], ignore_index=True)
fig.add_trace(go.Scatter(x=bridge_x, y=bridge_y, mode="lines+markers", name="Forecast", line=dict(color="#19b8a6", width=3, dash="dot"), marker=dict(size=7), fill="tozeroy", fillcolor="rgba(25,184,166,.08)"))
fig.update_layout(**chart_layout(), height=440, xaxis_title=None, yaxis_title=None, showlegend=True, legend=dict(orientation="h", y=1.12, x=0), hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Month-by-month projection")
view = forecast.copy()
view["Change vs prior month"] = view["Revenue"].pct_change() * 100
st.dataframe(view, use_container_width=True, hide_index=True, column_config={"Month": st.column_config.DateColumn(format="MMM YYYY"), "Revenue": st.column_config.NumberColumn(format="$%.2f"), "Change vs prior month": st.column_config.NumberColumn(format="%.1f%%")})
st.download_button("↓  Download forecast", view.to_csv(index=False).encode("utf-8"), "salesiq_forecast.csv", "text/csv")
st.info(f"Forecast method: {metrics['model']}. A chronological holdout is used for the reported MAE. Forecasts indicate trend scenarios, not guaranteed outcomes.")
st.caption("Only monthly revenue is forecast. Product cost data is not available to estimate future profit.")
