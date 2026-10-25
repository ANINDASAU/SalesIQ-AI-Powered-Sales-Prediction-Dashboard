"""Load and normalize sales records from MySQL, with a local Excel fallback."""

from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text

from src.db import engine
from src.preprocessing import clean_sales


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_EXCEL = PROJECT_ROOT / "data" / "raw" / "Online Retail.xlsx"


def _normalize_sales(df: pd.DataFrame) -> pd.DataFrame:
	"""Normalize source columns and calculate transaction revenue."""
	aliases = {
		"invoice_no": "InvoiceNo",
		"invoice_date": "InvoiceDate",
		"product_id": "StockCode",
		"product_name": "Description",
		"quantity": "Quantity",
		"unit_price": "UnitPrice",
		"country": "Country",
	}
	df = df.rename(columns={key: value for key, value in aliases.items() if key in df.columns})
	df = clean_sales(df)
	df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
	return df


@st.cache_data(ttl=300, show_spinner=False)
def load_sales_data() -> tuple[pd.DataFrame, str]:
	"""Prefer MySQL and fall back to the bundled source workbook."""
	database_error: Exception | None = None
	try:
		query = text("""
			SELECT s.invoice_no AS InvoiceNo,
				   s.invoice_date AS InvoiceDate,
				   s.product_id AS StockCode,
				   p.product_name AS Description,
				   s.quantity AS Quantity,
				   s.unit_price AS UnitPrice,
				   s.country AS Country
			FROM sales AS s
			JOIN products AS p ON p.product_id = s.product_id
			ORDER BY s.invoice_date
		""")
		with engine.connect() as connection:
			database_df = pd.read_sql_query(query, connection)
		if not database_df.empty:
			return _normalize_sales(database_df), "MySQL database"
	except Exception as exc:
		database_error = exc

	if RAW_EXCEL.exists():
		raw_df = pd.read_excel(RAW_EXCEL)
		return _normalize_sales(raw_df), "Local Excel dataset (MySQL unavailable)"

	message = "No sales data could be loaded. Configure MySQL or add data/raw/Online Retail.xlsx."
	if database_error:
		raise RuntimeError(message) from database_error
	raise RuntimeError(message)
