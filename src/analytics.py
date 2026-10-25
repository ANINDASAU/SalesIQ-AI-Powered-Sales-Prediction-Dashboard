import pandas as pd


def calculate_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "revenue": 0.0,
            "orders": 0,
            "units_sold": 0,
            "average_order_value": 0.0,
        }

    revenue = df["Revenue"].sum()
    orders = df["InvoiceNo"].nunique()
    units_sold = df["Quantity"].sum()

    return {
        "revenue": float(revenue),
        "orders": int(orders),
        "units_sold": int(units_sold),
        "average_order_value": (
            float(revenue / orders) if orders else 0.0
        ),
    }


def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Month", "Revenue", "Units_Sold"])

    result = df.copy()

    result["Month"] = (
        result["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    )

    result = (
        result.groupby("Month", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Units_Sold=("Quantity", "sum"),
        )
        .sort_values("Month")
    )
    if result.empty:
        return result

    complete_months = pd.date_range(result["Month"].min(), result["Month"].max(), freq="MS")
    result = result.set_index("Month").reindex(complete_months, fill_value=0)
    result.index.name = "Month"
    return result.reset_index()


def product_sales(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=["StockCode", "Description", "Revenue", "Units_Sold", "Orders"]
        )

    aggregations = {
        "Revenue": ("Revenue", "sum"),
        "Units_Sold": ("Quantity", "sum"),
        "Orders": ("InvoiceNo", "nunique"),
    }
    if "Description" in df.columns:
        aggregations["Description"] = ("Description", "first")

    return (
        df.groupby("StockCode", as_index=False)
        .agg(**aggregations)
        .sort_values("Revenue", ascending=False)
    )