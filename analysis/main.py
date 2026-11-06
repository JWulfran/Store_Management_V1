from .extract import extract_data
from .transform import clean_data, build_star_schema
from .load import load_data


def run_pipeline():
    # 1. Extract
    categories_df, products_df, purchases_df, sales_df = extract_data()

    # 2. Clean
    categories, products, purchases, sales = clean_data(
        categories_df,
        products_df,
        purchases_df,
        sales_df,
    )

    # 3. Build the analytical tables
    (dim_date, dim_product, dim_supplier, fact_sales, fact_purchases,) = build_star_schema(categories, products, purchases, sales,)

    # 4. Preview the results
    tables = {
        "dim_date": dim_date,
        "dim_product": dim_product,
        "dim_supplier": dim_supplier,
        "fact_sales": fact_sales,
        "fact_purchases": fact_purchases,
    }

    for name, frame in tables.items():
        print(f"\n{name}: {len(frame)} rows")
        print(frame.head())

    # 5. Load into SQL Server
    load_data(tables)
    print("\nPipeline completed successfully!")


if __name__ == "__main__":
    run_pipeline()