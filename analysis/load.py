# """Run from the Django project root: python -m analysis.load

# Loads a FULL SNAPSHOT into staging, using Windows authentication.
# The database must already exist. Run only one loader at a time.
# """

# import os
# from decimal import Decimal

# import pandas as pd
# from sqlalchemy import (
#     BigInteger, Boolean, Column, Date, ForeignKey, MetaData,
#     Numeric, Table, Unicode, create_engine, text,
# )
# from sqlalchemy.engine import URL


# def main():
#     # 1. Importing transform also runs extract and transform in your version.
#     from .transform import (
#         T_Categories_df, T_Products_df, T_Purchases_df, T_sales_df,
#     )

#     # 2. Connect to your ANALYTICS database, not the Django database.
#     server = os.environ.get("STORE_SQL_SERVER", r"localhost\SQLEXPRESS")
#     database = os.environ.get("STORE_SQL_DATABASE", "StoreAnalytics")
#     url = URL.create(
#         "mssql+pyodbc",
#         host=server,
#         database=database,
#         query={
#             "driver": "ODBC Driver 18 for SQL Server",
#             "Trusted_Connection": "yes",
#             "Encrypt": "yes",
#             # Local development with a self-signed server certificate.
#             "TrustServerCertificate": "yes",
#         },
#     )

#     # 3. Define tables. IDs come from Django: no SQL identity columns.
#     metadata = MetaData(schema="staging")
#     Table("categories", metadata,
#           Column("id", BigInteger, primary_key=True, autoincrement=False),
#           Column("name", Unicode(100), nullable=False))
#     Table("products", metadata,
#           Column("id", BigInteger, primary_key=True, autoincrement=False),
#           Column("sku", Unicode(25), nullable=False, unique=True),
#           Column("name", Unicode(255), nullable=False),
#           Column("category_id", BigInteger, ForeignKey("staging.categories.id"), nullable=False),
#           Column("purchase_price", Numeric(18, 2), nullable=False),
#           Column("selling_price", Numeric(18, 2), nullable=False),
#           Column("stock", BigInteger, nullable=False),
#           Column("is_active", Boolean, nullable=False))
#     for name, total in [("purchases", "total_cost"), ("sales", "revenue")]:
#         columns = [Column("id", BigInteger, primary_key=True, autoincrement=False)]
#         if name == "purchases":
#             columns.append(Column("supplier", Unicode(255), nullable=False))
#         columns.extend([
#             Column("product_id", BigInteger, ForeignKey("staging.products.id"), nullable=False),
#             Column("quantity", BigInteger, nullable=False),
#             Column("unit_price", Numeric(18, 2), nullable=False),
#             Column("date", Date, nullable=False),
#             Column(total, Numeric(18, 2), nullable=False),
#         ])
#         Table(name, metadata, *columns)

#     # 4. Copies keep the transformed DataFrames unchanged.
#     frames = {
#         "categories": T_Categories_df.copy(),
#         "products": T_Products_df.copy(),
#         "purchases": T_Purchases_df.copy(),
#         "sales": T_sales_df.copy(),
#     }
#     # Check before any DELETE, especially the less strict sales transform.
#     for name, frame in frames.items():
#         columns = list(metadata.tables[f"staging.{name}"].columns.keys())
#         frames[name] = frame = frame[columns].copy()
#         if frame.isna().any().any():
#             raise ValueError(f"{name}: missing values; fix transform.py first")
#         for column in [c for c in ["id", "category_id", "product_id", "quantity", "stock"] if c in frame]:
#             numbers = pd.to_numeric(frame[column], errors="raise")
#             minimum = 0 if column == "stock" else 1
#             if not ((numbers >= minimum) & (numbers % 1 == 0) & (numbers <= 9223372036854775807)).all():
#                 raise ValueError(f"{name}.{column}: invalid integer")
#             frame[column] = numbers.astype("int64")
#         if frame["id"].duplicated().any():
#             raise ValueError(f"{name}: duplicate IDs")
#         for column in [c for c in ["purchase_price", "selling_price", "unit_price", "total_cost", "revenue"] if c in frame]:
#             amounts = frame[column].map(lambda value: Decimal(str(value)))
#             if not all(value.is_finite() and 0 < value < Decimal("10000000000000000")
#                        and value == value.quantize(Decimal("0.01")) for value in amounts):
#                 raise ValueError(f"{name}.{column}: invalid amount or more than two decimals")
#             frame[column] = amounts
#         if "date" in frame:
#             frame["date"] = pd.to_datetime(frame["date"], format="%Y-%m-%d", errors="raise").dt.date
#         if name in ["purchases", "sales"]:
#             total = "total_cost" if name == "purchases" else "revenue"
#             if not (frame[total] == frame["quantity"] * frame["unit_price"]).all():
#                 raise ValueError(f"{name}: total does not match quantity times price")
#     if not frames["products"]["category_id"].isin(frames["categories"]["id"]).all():
#         raise ValueError("Products reference unknown categories")
#     for name in ["purchases", "sales"]:
#         if not frames[name]["product_id"].isin(frames["products"]["id"]).all():
#             raise ValueError(f"{name}: unknown products; fix transform.py first")

#     # 5. One transaction: either all four tables load, or all changes roll back.
#     engine = create_engine(url, fast_executemany=True)
#     try:
#         with engine.begin() as connection:
#             connection.execute(text("IF SCHEMA_ID('staging') IS NULL EXEC('CREATE SCHEMA staging')"))
#             metadata.create_all(connection)
#             # Delete children first to respect foreign keys.
#             for name in ["sales", "purchases", "products", "categories"]:
#                 connection.execute(text(f"DELETE FROM staging.{name}"))
#             # Insert parents first. Names are fixed above, never user input.
#             for name, frame in frames.items():
#                 frame.to_sql(name, con=connection, schema="staging",
#                              if_exists="append", index=False, chunksize=1000,
#                              dtype={c.name: c.type for c in metadata.tables[f"staging.{name}"].columns})
#                 count = connection.execute(text(f"SELECT COUNT_BIG(*) FROM staging.{name}")).scalar_one()
#                 if count != len(frame):
#                     raise ValueError(f"{name}: loaded row count mismatch")
#                 print(f"{name}: {count} rows checked (commit pending)")
#         print("Load completed: all four tables committed.")
#     finally:
#         engine.dispose()


# if __name__ == "__main__":
#     main()
