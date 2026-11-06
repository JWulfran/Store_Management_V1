# Store Management V1

A Django application for managing a small store’s product catalog, purchases, sales, and inventory. A dashboard summarizes business activity, while CSV exports connect operational data to a separate analytics workflow.

The interface primarily uses French labels. This version records one product per sale.

## Features

- **Product catalog:** browse products, search the list, and view SKUs, categories, prices, stock, and active status.
- **Administration:** manage categories and products through Django Admin.
- **Purchases:** record a supplier, product, quantity, unit price, and date; new purchases increase stock automatically.
- **Sales:** select an active product in stock, preview its selling price and total, and record the quantity and date. The server uses the product’s selling price and checks available stock.
- **Inventory:** automatically decrease stock for new sales and restore it when a sale is deleted.
- **Dashboard:** view revenue, purchase amounts, quantities, sales count, active products, low-stock and out-of-stock counts, and inventory value at purchase price. Includes six-month charts, five top-selling products, and recent transactions.
- **Demo data:** generate a realistic catalog and transactions in chronological order.
- **CSV exports:** export categories, products, purchases, and sales for analysis.
- **Analytics:** extract and clean CSV data, build a dimensional model, and load five analytical tables into SQL Server. An exploratory notebook is also included.

## Technology

| Layer | Tools |
| --- | --- |
| Backend | Python, Django, Django ORM |
| Database | SQLite for local development |
| Frontend | Django templates, HTML, CSS, JavaScript |
| Charts | Chart.js 4.5.0, loaded from a CDN |
| Demo data | Faker with the `fr_CA` locale |
| Configuration | python-dotenv and a root `.env` file |
| Analytics | Pandas, SQLAlchemy, pyodbc, SQL Server; notebook tooling |

## Getting started

Run all commands from the project root, where `manage.py` is located.

### 1. Clone the repository

```bash
git clone https://github.com/JWulfran/Store_Management_V1.git
cd Store_Management_V1
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Dependency note:** the committed requirements file is UTF-16 encoded and pins `Django==6.1.1`, `Faker==40.41.0`, and supporting packages. These pins are recorded here as repository values; a successful installation has not been verified. If pip reports that a pinned version is unavailable, review and correct the dependency pins using releases available for your Python version before continuing. If an editor or package tool has trouble reading the file, save it as UTF-8. The repository does not declare a Python version.

### 4. Configure the Django secret

Create a `.env` file in the project root, alongside `manage.py`:

```dotenv
Django_key=replace_with_your_generated_secret
```

Generate a secret and copy the output into `Django_key`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

The variable name is case-sensitive. `config/settings.py` loads this file with `python-dotenv` and reads `Django_key` as the Django secret key. Keep `.env` private; it is already ignored by Git.

**Additional dependency:** the current requirements file does not include `python-dotenv`, even though settings import it. Install it before running Django commands:

```bash
python -m pip install python-dotenv
```

### 5. Initialize the database

```bash
python manage.py migrate
python manage.py createsuperuser
```

SQLite creates `db.sqlite3` locally. No separate database server is required for the Django application. SQL Server is used only by the optional analytics pipeline.

### 6. Start the application

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

| Page | Local URL |
| --- | --- |
| Dashboard | `/` |
| Products | `/products/` |
| Purchases | `/purchases/` |
| New purchase | `/purchases/add/` |
| Sales | `/sales/` |
| New sale | `/sales/add/` |
| Django Admin | `/admin/` |

Dashboard charts require an internet connection to load Chart.js from its CDN.

## Typical workflow

1. Sign in to Django Admin with the superuser account.
2. Create categories and products, including purchase and selling prices. Start new products at zero stock if you want stock to reflect recorded purchases and sales.
3. Record purchases to replenish inventory.
4. Record sales; the form offers active products with stock available.
5. Review the dashboard and export data when needed.

The low-stock threshold is currently fixed at **10 units or fewer** for active products. Inventory value is calculated across all products as `stock × purchase_price`.

## Generate demo data

Use a development database for generated data:

```bash
python manage.py generate_test_data
```

The built-in catalog contains **37 products across 8 categories**. By default, the command creates **200 purchases** and **500 sales** over a **365-day lookback window**.

Customize the transaction counts and period:

```bash
python manage.py generate_test_data --days 180 --purchases 100 --sales 250
```

Transactions are processed by date, with purchases before sales on the same day. The generator can bring a future purchase forward when replenishment is needed. Repeated runs reuse catalog products and categories, update some product attributes, and add more transactions.

**Known limitation:** the command exposes a `--clear` flag, but its `clear_data()` method is missing. That option currently raises an error and should not be used until implemented.

## Export data

```bash
python manage.py export_data
```

The command writes UTF-8-with-BOM CSV files into `exports/`, replacing existing files with the same names.

| File | Contents |
| --- | --- |
| `categories.csv` | Category IDs and names |
| `products.csv` | SKUs, category references, prices, stock, and active status |
| `purchases.csv` | Supplier, product, quantity, price, date, and total cost |
| `sales.csv` | Product, quantity, price, date, and revenue |

Totals use `quantity × unit_price`. Run the export again to refresh the analytics inputs after changing store data.

## Analytics pipeline and SQL Server

The operational application uses SQLite. The analytics pipeline reads CSV snapshots from `exports/`, cleans them, builds dimensions and facts, and loads them into a separate SQL Server database.

### 1. Prepare the analytics dependencies

Pandas and notebook-related packages are included in the current requirements file. The loader also imports SQLAlchemy and uses pyodbc; neither is currently listed there:

```bash
python -m pip install sqlalchemy pyodbc
```

Install the Microsoft ODBC driver for SQL Server on the machine running the pipeline. It is a system dependency, separate from the Python packages. The driver name in `.env` must match an installed driver.

### 2. Configure the SQL Server connection

Create the target SQL Server database before loading, then add these settings to the same root `.env` file:

```dotenv
# Required by the Django application
Django_key=replace_with_your_generated_secret

# Required only for the analytics load; replace these example values
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=StoreAnalytics
DB_DRIVER=ODBC Driver 18 for SQL Server
```

The loader uses Windows integrated authentication (`Trusted_Connection=yes`), encryption, and `TrustServerCertificate=yes`. It does not currently read a SQL username or password. The executing account needs access to the target database and permission to create, drop, and insert into tables. Other authentication methods require changes to `analysis/load.py`.

### 3. Export and run the pipeline

Run these commands from the project root:

```bash
python manage.py export_data
python -m analysis.main
```

`analysis.main` runs the complete workflow:

1. `extract_data()` reads categories, products, purchases, and sales CSV files and prints row counts.
2. `clean_data()` cleans category and product identifiers and names, removes invalid relationships and duplicate records, validates transaction quantities, prices, dates, and supplier names, and recalculates transaction amounts.
3. `build_star_schema()` creates three dimensions and two fact tables.
4. The pipeline prints table counts and previews.
5. `load_data()` writes all five tables to SQL Server’s `dbo` schema using a SQLAlchemy transaction.

**Replacement behavior:** each load uses `if_exists="replace"`. It drops and recreates the five destination tables rather than appending rows or performing incremental updates. Use a dedicated analytics database; existing data and table-level constraints or indexes on these tables can be lost. The loader does not explicitly define SQL primary keys, foreign keys, or financial column types.

The pipeline reads the last CSV export, not the live SQLite database. Export again after store transactions change. Running `python -m analysis.extract` or `python -m analysis.transform` alone does not run the workflow: these modules currently define functions without command-line entry points.

### Analytical tables

| Table | Grain / purpose | Columns |
| --- | --- | --- |
| `dim_date` | One row per date present in purchases or sales | `date_id`, `date`, `year`, `quarter`, `month`, `day` |
| `dim_product` | One row per cleaned product; includes category name | `product_id`, `sku`, `product_name`, `category_name` |
| `dim_supplier` | One row per distinct cleaned purchase supplier name | `supplier_id`, `supplier_name` |
| `fact_sales` | One row per cleaned sale record | `sale_id`, `date_id`, `product_id`, `quantity`, `unit_price`, `revenue` |
| `fact_purchases` | One row per cleaned purchase record | `purchase_id`, `date_id`, `product_id`, `supplier_id`, `quantity`, `unit_price`, `total_cost` |

Both fact tables share the date and product dimensions. Purchases also reference the supplier dimension. `date_id` uses `YYYYMMDD`; supplier IDs are regenerated from sorted supplier names on every run and may change when suppliers change. The date dimension contains transaction dates only, rather than a continuous calendar.

`analysis/Store_analysis.ipynb` is included for notebook-based exploration. SQL Server is optional for running the store application but required for the full `analysis.main` command.

## Project structure

```text
Store_Management_V1/
├── config/                 # Django settings and root URL configuration
├── products/               # Categories, products, admin, management commands
├── purchases/              # Purchase forms, views, and stock-increase signal
├── sales/                  # Sale forms, views, and stock signals
├── dashboard/              # KPI aggregation and dashboard view
├── templates/              # Shared layout and application templates
├── static/                 # CSS and JavaScript
├── analysis/               # ETL pipeline, dimensional model, SQL loader, notebook
├── exports/                # CSV datasets and export output
├── manage.py
├── requirements.txt
└── README.md
```

## Data model

| Model | Main fields | Relationships |
| --- | --- | --- |
| Category | Name, description, timestamps | One category has many products |
| Product | SKU, name, purchase price, selling price, stock, active status | Belongs to a category |
| Purchase | Supplier, quantity, unit price, date | References a product |
| Sale | Quantity, unit price, date | References a product |

Category and product references use protected deletion. Stock adjustments run through Django signals when new purchases and sales are saved. Deleting a sale restores its quantity. Editing existing transactions does not reconcile stock, and deleting a purchase does not reverse its stock increase. Review these behaviors before changing historical transactions through the admin or scripts. Bulk operations that bypass save signals also bypass the creation-time stock adjustments.

## Development checks

After installing compatible dependencies:

```bash
python manage.py check
python manage.py test
```

The app test modules currently contain scaffolding rather than substantive tests. Passing these commands alone does not validate inventory behavior. Manually verify that a purchase increases stock, a sale decreases it, an oversized sale is rejected, and the dashboard and exports reflect the transactions.

## Current scope and next steps

This version provides a foundation for store operations and analytics. Potential extensions include:

- Multi-product carts, receipts, and a full point-of-sale workflow.
- Barcode scanning and payment-provider integrations.
- Staff authentication and role-based permissions for operational pages.
- Stock reconciliation for edited and deleted transactions.
- A working demo-data cleanup command and automated inventory tests.
- Incremental analytics loads, explicit SQL keys and types, and a reproducible dependency setup.

These extensions are not implemented in the current repository.

## Deployment considerations

The committed settings are for local development: `DEBUG=True`, an environment-based secret key, and an empty `ALLOWED_HOSTS` list. Before deployment, configure a private production secret, disable debug mode, set allowed hosts, configure static-file serving, and protect operational routes with appropriate authentication and permissions. The current store views do not enforce login.

## Contributing

1. Create a branch for your change, such as `feature/inventory-tests`.
2. Keep changes focused and document any setup or behavior changes.
3. Run relevant checks and verify the affected workflow.
4. Open a pull request explaining the change and how it was validated.

Avoid committing virtual environments, local databases, credentials, or exports containing private business data.

## Author

Developed by [JWulfran](https://github.com/JWulfran).

## License

No license file is currently included in this repository. Contact the author for permission and terms before redistributing or reusing the code.
