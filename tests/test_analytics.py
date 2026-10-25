import pandas as pd

from src.analytics import calculate_kpis, monthly_sales, product_sales


def sample_sales() -> pd.DataFrame:
    return pd.DataFrame({
        "InvoiceNo": ["100", "100", "101"],
        "InvoiceDate": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-03-01"]),
        "StockCode": ["A", "B", "A"],
        "Description": ["Alpha", "Beta", "Alpha"],
        "Quantity": [2, 1, 3],
        "UnitPrice": [10.0, 5.0, 10.0],
        "Revenue": [20.0, 5.0, 30.0],
    })


def test_kpis_use_distinct_invoices_and_revenue():
    assert calculate_kpis(sample_sales()) == {
        "revenue": 55.0,
        "orders": 2,
        "units_sold": 6,
        "average_order_value": 27.5,
    }


def test_monthly_sales_includes_months_without_transactions():
    result = monthly_sales(sample_sales())
    assert result["Revenue"].tolist() == [25.0, 0.0, 30.0]
    assert result["Units_Sold"].tolist() == [3, 0, 3]


def test_product_sales_includes_names_and_orders():
    result = product_sales(sample_sales()).set_index("StockCode")
    assert result.loc["A", "Description"] == "Alpha"
    assert result.loc["A", "Revenue"] == 50.0
    assert result.loc["A", "Orders"] == 2


def test_empty_sales_return_stable_empty_results():
    empty = sample_sales().iloc[0:0]
    assert calculate_kpis(empty)["revenue"] == 0.0
    assert monthly_sales(empty).empty
    assert product_sales(empty).empty