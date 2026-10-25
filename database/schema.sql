-- SalesIQ MySQL schema. Safe to run repeatedly; existing tables are preserved.
CREATE DATABASE IF NOT EXISTS sales_dashboard
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sales_dashboard;

CREATE TABLE IF NOT EXISTS products (
  product_id VARCHAR(64) NOT NULL,
  product_name VARCHAR(512) NOT NULL,
  PRIMARY KEY (product_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sales (
  sale_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  source_key CHAR(64) NOT NULL,
  invoice_no VARCHAR(32) NOT NULL,
  invoice_date DATETIME NOT NULL,
  product_id VARCHAR(64) NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(12, 4) NOT NULL,
  country VARCHAR(128) NOT NULL DEFAULT 'Unknown',
  PRIMARY KEY (sale_id),
  UNIQUE KEY uq_sales_source_key (source_key),
  KEY idx_sales_invoice_date (invoice_date),
  KEY idx_sales_product_date (product_id, invoice_date),
  CONSTRAINT fk_sales_product
    FOREIGN KEY (product_id) REFERENCES products (product_id)
) ENGINE=InnoDB;