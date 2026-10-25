import pandas as pd
import pytest

from src.preprocessing import clean_sales


def test_clean_sales_drops_invalid_cancelled_and_non_sale_rows():
    raw = pd.DataFrame({
        "InvoiceNo": ["1001", "1002", "C1003", "1004", "1005"],
        "InvoiceDate": ["2025-01-10", "2025-01-11", "2025-01-12", "invalid", "2025-01-13"],
        "StockCode": ["P01", "P02", "P03", "P04", "P05"],
        "Quantity": [2, 3, 1, 1, -2],
        "UnitPrice": [100, 50, 25, 25, 10],
    })
    cleaned = clean_sales(raw)
    assert len(cleaned) == 2
    assert cleaned["Revenue"].sum() == 350
    assert cleaned["Country"].eq("Unknown").all()


def test_clean_sales_requires_transaction_columns():
    with pytest.raises(ValueError, match="Missing columns"):
        clean_sales(pd.DataFrame({"InvoiceNo": ["1"]}))