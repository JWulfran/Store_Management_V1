import pandas as pd
from .extract import extract_data

def transform_data(categories_df, products_df, purchases_df, sales_df):
    # Copies pour conserver les données d'origine
    T_Categories_df = categories_df.copy()
    T_Products_df = products_df.copy()
    T_Purchases_df = purchases_df.copy()
    T_sales_df = sales_df.copy()

    # =====================================
    # TRANSFORM CATEGORIES
    # =====================================

    # Convert IDs into numbers
    T_Categories_df["id"] = pd.to_numeric(
        T_Categories_df["id"],
        errors="coerce"
    )

    # Remove spaces around names
    T_Categories_df["name"] = T_Categories_df["name"].astype("string").str.strip()

    # Remove missing IDs and names
    T_Categories_df = T_Categories_df.dropna(subset=["id", "name"])

    # Keep positive, whole-number IDs and non-empty names
    T_Categories_df = T_Categories_df[
        (T_Categories_df["id"] > 0) &
        (T_Categories_df["id"] % 1 == 0) &
        (T_Categories_df["name"] != "")
    ].copy()

    # Store IDs as integers
    T_Categories_df["id"] = T_Categories_df["id"].astype("int64")

    # Keep the first occurrence of each ID
    T_Categories_df = T_Categories_df.drop_duplicates(subset=["id"])

    # =====================================
    # TRANSFORM PRODUCTS
    # =====================================

    # Clean text columns
    T_Products_df["sku"] = T_Products_df["sku"].astype("string").str.strip()
    T_Products_df["name"] = T_Products_df["name"].astype("string").str.strip()

    # Convert numeric columns
    numeric_columns = [
        "id",
        "category_id",
        "purchase_price",
        "selling_price",
        "stock"
    ]

    for column in numeric_columns:
        T_Products_df[column] = pd.to_numeric(
            T_Products_df[column],
            errors="coerce"
        )

    # Convert active status into Boolean values
    T_Products_df["is_active"] = (
        T_Products_df["is_active"]
        .astype("string")
        .str.strip()
        .str.lower()
        .map({
            "true": True,
            "false": False
        })
    )

    # Remove missing or unrecognized values
    T_Products_df = T_Products_df.dropna(
        subset=[
            "id",
            "sku",
            "name",
            "category_id",
            "purchase_price",
            "selling_price",
            "stock",
            "is_active"
        ]
    )

    # Keep rows that meet the rules
    T_Products_df = T_Products_df[
        (T_Products_df["id"] > 0) &
        (T_Products_df["id"] % 1 == 0) &
        (T_Products_df["category_id"] > 0) &
        (T_Products_df["category_id"] % 1 == 0) &
        (T_Products_df["sku"] != "") &
        (T_Products_df["name"] != "") &
        (T_Products_df["purchase_price"] > 0) &
        (T_Products_df["selling_price"] > 0) &
        (T_Products_df["stock"] >= 0) &
        (T_Products_df["stock"] % 1 == 0)
    ].copy()

    # Keep only products referencing a cleaned category
    T_Products_df = T_Products_df[
        T_Products_df["category_id"].isin(T_Categories_df["id"])
    ].copy()

    # Convert whole-number columns into integers
    for column in ["id", "category_id", "stock"]:
        T_Products_df[column] = T_Products_df[column].astype("int64")

    T_Products_df["is_active"] = T_Products_df["is_active"].astype(bool)

    # Remove duplicate IDs and SKUs
    T_Products_df = T_Products_df.drop_duplicates(subset=["id"])
    T_Products_df = T_Products_df.drop_duplicates(subset=["sku"])

    # =====================================
    # TRANSFORM PURCHASES
    # =====================================

    # Clean supplier names
    T_Purchases_df["supplier"] = (
        T_Purchases_df["supplier"]
        .astype("string")
        .str.strip()
    )

    # Convert numeric columns
    for column in ["id", "product_id", "quantity", "unit_price"]:
        T_Purchases_df[column] = pd.to_numeric(
            T_Purchases_df[column],
            errors="coerce"
        )

    # Convert dates
    T_Purchases_df["date"] = pd.to_datetime(
        T_Purchases_df["date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    # Remove missing or invalid values
    T_Purchases_df = T_Purchases_df.dropna(
        subset=[
            "id",
            "supplier",
            "product_id",
            "quantity",
            "unit_price",
            "date"
        ]
    )

    # Keep positive, whole-number IDs and quantities
    T_Purchases_df = T_Purchases_df[
        (T_Purchases_df["id"] > 0) &
        (T_Purchases_df["id"] % 1 == 0) &
        (T_Purchases_df["product_id"] > 0) &
        (T_Purchases_df["product_id"] % 1 == 0) &
        (T_Purchases_df["quantity"] > 0) &
        (T_Purchases_df["quantity"] % 1 == 0) &
        (T_Purchases_df["unit_price"] > 0) &
        (T_Purchases_df["supplier"] != "")
    ].copy()

    # Keep only purchases referencing a cleaned product
    T_Purchases_df = T_Purchases_df[
        T_Purchases_df["product_id"].isin(T_Products_df["id"])
    ].copy()

    # Convert whole-number columns into integers
    for column in ["id", "product_id", "quantity"]:
        T_Purchases_df[column] = T_Purchases_df[column].astype("int64")

    # Remove duplicate purchase IDs
    T_Purchases_df = T_Purchases_df.drop_duplicates(subset=["id"])

    # Calculate the total cost
    T_Purchases_df["total_cost"] = (
        T_Purchases_df["quantity"] * T_Purchases_df["unit_price"]
    ).round(2)

    # Format dates for CSV export
    T_Purchases_df["date"] = T_Purchases_df["date"].dt.strftime("%Y-%m-%d")


    # =====================================
    # TRANSFORM SALES
    # =====================================

    # Remove rows with missing essential values
    T_sales_df = sales_df.dropna(subset=["id","product_id", "quantity", "unit_price", "date"])

    # Remove duplicate IDs
    T_sales_df = T_sales_df.drop_duplicates(subset=["id"], keep="first")

    # Convert numeric columns
    T_sales_df["quantity"] = pd.to_numeric(T_sales_df["quantity"], errors="coerce")
    T_sales_df["unit_price"] = pd.to_numeric(T_sales_df["unit_price"], errors="coerce")
        # Remove invalid numeric values
    T_sales_df = T_sales_df.dropna(subset=["quantity", "unit_price"])

    # Keep only positive quantities and prices
    T_sales_df = T_sales_df[(T_sales_df["quantity"] > 0) & (T_sales_df["unit_price"] > 0)].copy()

    # Convert dates
    T_sales_df["date"] = pd.to_datetime(T_sales_df["date"], errors="coerce")
        # Remove invalid dates
    T_sales_df = T_sales_df.dropna(subset=["date"])

    # Recalculate the revenue
    T_sales_df["revenue"] = (T_sales_df["quantity"] * T_sales_df["unit_price"]).round(2)

    # Format dates 
    T_sales_df["date"] = T_sales_df["date"].dt.strftime("%Y-%m-%d") 

    return (
        T_Categories_df,
        T_Products_df,
        T_Purchases_df,
        T_sales_df,
    )


def main():
    from .extract import extract_data

    categories_df, products_df, purchases_df, sales_df = extract_data()

    return transform_data(
        categories_df,
        products_df,
        purchases_df,
        sales_df,
    )


if __name__ == "__main__":
    main()

    categories_df, products_df, purchases_df, sales_df = extract_data()

    T_Categories_df, T_Products_df, T_Purchases_df, T_sales_df = transform_data(categories_df, products_df, purchases_df, sales_df)

    T_datasets = {
    "Transormed Category" : [len(T_Categories_df), len(categories_df)], 
    "Transormed Product" : [len(T_Products_df), len(products_df)],
    "Transormed Purchase" : [len(T_Purchases_df), len(purchases_df)],
    "Transormed Sales" : [len(T_sales_df), len(sales_df)]
    }

    # T_datasets = {
    # "Transormed Category" : [T_Categories_df, categories_df], 
    # "Transormed Product" : [T_Products_df, products_df],
    # "Transormed Purchase" : [T_Purchases_df, purchases_df],
    # "Transormed Sales" : [T_sales_df, sales_df]
    # }

    # print(T_datasets.items())
    for name,[len_1, len_2] in T_datasets.items():
            print(f"\n{name} — original rows: {len_2}")
            print(f"{name} — cleaned rows : {len_1}")
