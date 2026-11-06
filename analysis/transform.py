import pandas as pd


def clean_data(categories_df, products_df, purchases_df, sales_df):
    # Copies preserve the original DataFrames
    categories = categories_df.copy()
    products = products_df.copy()
    purchases = purchases_df.copy()
    sales = sales_df.copy()

    # =====================================
    # 1. CATEGORIES
    # =====================================

    categories["id"] = pd.to_numeric(categories["id"], errors="coerce")
    categories["name"] = (categories["name"].astype("string").str.strip())
    categories = categories.dropna(subset=["id", "name"])
    categories = categories[(categories["id"] > 0) & (categories["id"] % 1 == 0) & (categories["name"] != "")].copy()
    categories["id"] = categories["id"].astype("int64")
    categories = categories.drop_duplicates(subset=["id"])

    # =====================================
    # 2. PRODUCTS
    # =====================================

    for column in ["sku", "name"]:
        products[column] = (products[column].astype("string").str.strip())

    products["id"] = pd.to_numeric(products["id"], errors="coerce")
    products["category_id"] = pd.to_numeric(products["category_id"], errors="coerce")
    products = products.dropna(subset=["id", "category_id", "sku", "name"])
    products = products[
        (products["id"] > 0) & (products["id"] % 1 == 0) & (products["category_id"] > 0) & (products["category_id"] % 1 == 0)
      & (products["sku"] != "") & (products["name"] != "")
    ].copy()

    # Keep products belonging to a valid category
    products = products[products["category_id"].isin(categories["id"])].copy()

    for column in ["id", "category_id"]:
        products[column] = products[column].astype("int64")

    products = products.drop_duplicates(subset=["id"])
    products = products.drop_duplicates(subset=["sku"])

    # =====================================
    # 3. PURCHASES AND SALES
    # =====================================

    # These tables share most cleaning rules
    transactions = {
        "purchases": purchases,
        "sales": sales,
    }

    for name, frame in transactions.items():
        original_count = len(frame)

        # Convert numeric values
        for column in ["id", "product_id", "quantity", "unit_price"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

        # Convert dates
        frame["date"] = pd.to_datetime(frame["date"], format="%Y-%m-%d", errors="coerce",)

        frame = frame.dropna(subset=["id", "product_id", "quantity", "unit_price", "date"])

        # IDs and quantities must be positive whole numbers
        for column in ["id", "product_id", "quantity"]:
            frame = frame[
                        (frame[column] > 0) & (frame[column] % 1 == 0)
                    ].copy()

            frame[column] = frame[column].astype("int64")

        # Keep finite, positive prices with at most two decimals
        frame = frame[
            (frame["unit_price"] > 0) & (frame["unit_price"] < float("inf")) & ((frame["unit_price"] * 100) - (frame["unit_price"] * 100).round()).abs().lt(0.000001)
        ].copy()

        frame["unit_price"] = frame["unit_price"].round(2)

        # Keep transactions referencing a valid product
        frame = frame[
            frame["product_id"].isin(products["id"])
        ].copy()

        # Supplier is required only for purchases
        if name == "purchases":
            frame["supplier"] = (
                frame["supplier"].astype("string").str.strip()
            )

            frame = frame.dropna(subset=["supplier"])
            frame = frame[frame["supplier"] != ""].copy()

        frame = frame.drop_duplicates(subset=["id"])

        # Recalculate the transaction amount
        total_column = "total_cost" if name == "purchases" else "revenue"

        frame[total_column] = (
            frame["quantity"] * frame["unit_price"]
        ).round(2)

        transactions[name] = frame

        print(
            f"{name}: {original_count} original rows, "
            f"{len(frame)} clean rows"
        )

    print("Clean categories:", len(categories))
    print("Clean products:", len(products))

    return (
        categories,
        products,
        transactions["purchases"],
        transactions["sales"],
    )

def build_star_schema(categories, products, purchases, sales):
    # =====================================
    # 1. DATE DIMENSION
    # =====================================

    # Collect dates from both transaction tables
    dates = pd.concat(
        [sales["date"], purchases["date"]],
        ignore_index=True,
    )

    dim_date = dates.to_frame(name="date")

    dim_date = (
        dim_date.drop_duplicates()
        .sort_values("date")
        .reset_index(drop=True)
    )

    # Example: 2026-09-03 becomes 20260903
    dim_date["date_id"] = (
        dim_date["date"].dt.strftime("%Y%m%d").astype("int64")
    )

    dim_date["year"] = dim_date["date"].dt.year
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["day"] = dim_date["date"].dt.day

    dim_date = dim_date[
        ["date_id", "date", "year", "quarter", "month", "day"]
    ]

    # =====================================
    # 2. PRODUCT DIMENSION
    # =====================================

    category_names = categories[["id", "name"]].rename(
        columns={
            "id": "category_id",
            "name": "category_name",
        }
    )

    dim_product = products[
        ["id", "sku", "name", "category_id"]
    ].copy()

    # Add the category name to each product
    dim_product = dim_product.merge(
        category_names,
        on="category_id",
        how="left",
        validate="many_to_one",
    )

    dim_product = dim_product.rename(
        columns={
            "id": "product_id",
            "name": "product_name",
        }
    )

    dim_product = dim_product[
        ["product_id", "sku", "product_name", "category_name"]
    ]

    # =====================================
    # 3. SUPPLIER DIMENSION
    # =====================================

    dim_supplier = (
        purchases[["supplier"]]
        .drop_duplicates()
        .sort_values("supplier")
        .reset_index(drop=True)
    )

    dim_supplier["supplier_id"] = dim_supplier.index + 1

    dim_supplier = dim_supplier.rename(
        columns={"supplier": "supplier_name"}
    )

    dim_supplier = dim_supplier[
        ["supplier_id", "supplier_name"]
    ]

    # =====================================
    # 4. SALES FACT TABLE
    # =====================================

    fact_sales = sales[
        ["id", "date", "product_id", "quantity", "unit_price", "revenue"]
    ].copy()

    fact_sales = fact_sales.merge(
        dim_date[["date", "date_id"]],
        on="date",
        how="left",
        validate="many_to_one",
    )

    fact_sales = fact_sales.rename(columns={"id": "sale_id"})

    fact_sales = fact_sales[
        ["sale_id", "date_id", "product_id", "quantity", "unit_price", "revenue"]
    ]

    # =====================================
    # 5. PURCHASES FACT TABLE
    # =====================================

    fact_purchases = purchases[
        ["id", "date", "product_id", "supplier",
         "quantity", "unit_price", "total_cost"]
    ].copy()

    fact_purchases = fact_purchases.merge(
        dim_date[["date", "date_id"]],
        on="date",
        how="left",
        validate="many_to_one",
    )

    fact_purchases = fact_purchases.merge(
        dim_supplier,
        left_on="supplier",
        right_on="supplier_name",
        how="left",
        validate="many_to_one",
    )

    fact_purchases = fact_purchases.rename(
        columns={"id": "purchase_id"}
    )

    fact_purchases = fact_purchases[
        ["purchase_id", "date_id", "product_id", "supplier_id",
         "quantity", "unit_price", "total_cost"]
    ]

    print("\nStar schema built!")

    return dim_date, dim_product, dim_supplier, fact_sales, fact_purchases