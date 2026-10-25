"""Import the bundled Online Retail workbook into the SalesIQ MySQL schema."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd
from sqlalchemy import inspect, text

from src.db import engine
from src.preprocessing import clean_sales


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = PROJECT_ROOT / "data" / "raw" / "Online Retail.xlsx"
CHUNK_SIZE = 2_000


def import_sales(file_path: Path = DEFAULT_FILE) -> tuple[int, int]:
    """Load clean product and sales records; source keys make reruns idempotent."""
    if not file_path.exists():
        raise FileNotFoundError(f"Sales workbook was not found: {file_path}")

    raw = pd.read_excel(file_path)
    clean = clean_sales(raw)
    clean["SourceKey"] = [
        hashlib.sha256(f"{file_path.name}:{row_index}".encode("utf-8")).hexdigest()
        for row_index in clean.index
    ]
    clean["StockCode"] = clean["StockCode"].astype(str)
    clean["Description"] = clean["Description"].fillna(clean["StockCode"]).astype(str)
    clean["Country"] = clean["Country"].fillna("Unknown").astype(str)
    clean["InvoiceNo"] = clean["InvoiceNo"].astype(str)

    products = clean[["StockCode", "Description"]].drop_duplicates("StockCode")
    product_rows = [
        {"product_id": row.StockCode, "product_name": row.Description[:512]}
        for row in products.itertuples(index=False)
    ]
    insert_product = text("""
        INSERT INTO products (product_id, product_name)
        VALUES (:product_id, :product_name)
        ON DUPLICATE KEY UPDATE product_name = VALUES(product_name)
    """)
    insert_sale = text("""
        INSERT IGNORE INTO sales
            (source_key, invoice_no, invoice_date, product_id, quantity, unit_price, country)
        VALUES
            (:source_key, :invoice_no, :invoice_date, :product_id, :quantity, :unit_price, :country)
    """)

    imported = 0
    with engine.begin() as connection:
        # Upgrade older Workbench schemas in place, without discarding existing sales.
        sales_columns = {column["name"] for column in inspect(connection).get_columns("sales")}
        if "source_key" not in sales_columns:
            connection.execute(text("ALTER TABLE sales ADD COLUMN source_key CHAR(64) NULL"))
            connection.execute(text(
                "UPDATE sales SET source_key = SHA2(CONCAT('legacy:', sale_id), 256) "
                "WHERE source_key IS NULL"
            ))
            connection.execute(text("ALTER TABLE sales MODIFY source_key CHAR(64) NOT NULL"))
        sales_indexes = inspect(connection).get_indexes("sales")
        if not any("source_key" in index.get("column_names", []) and index.get("unique") for index in sales_indexes):
            connection.execute(text(
                "CREATE UNIQUE INDEX uq_sales_source_key ON sales (source_key)"
            ))

        for offset in range(0, len(product_rows), CHUNK_SIZE):
            connection.execute(insert_product, product_rows[offset : offset + CHUNK_SIZE])

        columns = ["SourceKey", "InvoiceNo", "InvoiceDate", "StockCode", "Quantity", "UnitPrice", "Country"]
        records = clean[columns].rename(columns={
            "SourceKey": "source_key",
            "InvoiceNo": "invoice_no",
            "InvoiceDate": "invoice_date",
            "StockCode": "product_id",
            "Quantity": "quantity",
            "UnitPrice": "unit_price",
            "Country": "country",
        })
        for offset in range(0, len(records), CHUNK_SIZE):
            batch = records.iloc[offset : offset + CHUNK_SIZE].to_dict("records")
            result = connection.execute(insert_sale, batch)
            imported += max(result.rowcount, 0)

    return len(product_rows), imported


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", nargs="?", type=Path, default=DEFAULT_FILE)
    args = parser.parse_args()
    product_count, sale_count = import_sales(args.workbook)
    print(f"Products available: {product_count:,}")
    print(f"New sales imported: {sale_count:,} (existing source rows are skipped)")