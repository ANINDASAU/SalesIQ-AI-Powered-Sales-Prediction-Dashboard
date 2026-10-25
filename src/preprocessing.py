import pandas as pd


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    required = [
        "InvoiceNo",
        "InvoiceDate",
        "StockCode",
        "Quantity",
        "UnitPrice",
    ]

    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = df.copy()

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )
    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"], errors="coerce"
    )

    df = df.dropna(
        subset=[
            "InvoiceNo",
            "InvoiceDate",
            "StockCode",
            "Quantity",
            "UnitPrice",
        ]
    )

    # Cancelled invoices and non-sale adjustments are not revenue.
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C", na=False)]
    df = df[(df["UnitPrice"] > 0) & (df["Quantity"] > 0)].copy()

    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    if "Description" not in df.columns:
        df["Description"] = df["StockCode"].astype(str)
    if "Country" not in df.columns:
        df["Country"] = "Unknown"

    return df