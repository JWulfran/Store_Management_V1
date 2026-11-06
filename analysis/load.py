import os
from dotenv import load_dotenv
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def load_data(tables):

    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(base_dir / ".env")

    # 1. Prepare the connection
    url = URL.create(
        "mssql+pyodbc",
        host=os.environ.get("DB_SERVER"),
        database=os.environ.get("DB_NAME"),
        query={
            "driver": os.environ.get("DB_DRIVER"),
            "Trusted_Connection": "yes",
            "Encrypt": "yes",
            "TrustServerCertificate": "yes",
        },
    )

    engine = create_engine(url)

    try:
        # 2. Load all tables in one transaction
        with engine.begin() as connection:
            for name, frame in tables.items():
                print(f"Loading {name}: {len(frame)} rows")

                frame.to_sql(
                    name=name,
                    con=connection,
                    schema="dbo",
                    if_exists="replace",
                    index=False,
                    chunksize=1000,
                )

        print("\nLoading completed!")

    finally:
        # 3. Release the connections
        engine.dispose()