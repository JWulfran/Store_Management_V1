
from pathlib import Path

import pandas as pd


def extract_data():
    base_dir = Path(__file__).resolve().parent.parent
    export_dir = base_dir / "exports"

    categories_df = pd.read_csv(export_dir / "categories.csv")
    products_df = pd.read_csv(export_dir / "products.csv")
    purchases_df = pd.read_csv(export_dir / "purchases.csv")
    sales_df = pd.read_csv(export_dir / "sales.csv")

      # Display the number of extracted rows
    print("Categories:", len(categories_df))
    print("Products:", len(products_df))
    print("Purchases:", len(purchases_df))
    print("Sales:", len(sales_df))

    return categories_df, products_df, purchases_df, sales_df