
from pathlib import Path

import pandas as pd


def extract_data():
    base_dir = Path(__file__).resolve().parent.parent
    export_dir = base_dir / "exports"

    categories_df = pd.read_csv(export_dir / "categories.csv")
    products_df = pd.read_csv(export_dir / "products.csv")
    purchases_df = pd.read_csv(export_dir / "purchases.csv")
    sales_df = pd.read_csv(export_dir / "sales.csv")

    return categories_df, products_df, purchases_df, sales_df


if __name__ == "__main__":

    categories_df, products_df, purchases_df, sales_df = extract_data()

    datasets = {
        "Categories": categories_df,
        "Products": products_df,
        "Purchases": purchases_df,
        "Sales": sales_df
    }

    for name, df in datasets.items():

        print(f"\n{'=' * 50}")
        print(f"Original Dataset: {name}")
        print(f"{'=' * 50}")

        print(df.head())

        print(f"\nNumber of Rows: {len(df)}")
        print(f"Number of Columns: {len(df.columns)}")

        print(f"Missing Values: {df.isnull().sum().sum()}")
        print(f"Duplicate Rows: {df.duplicated().sum()}")

        if "id" in df.columns:
            print(f"Duplicate IDs: {df['id'].dropna().duplicated().sum()}")
