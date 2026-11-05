import csv
import os

from django.core.management.base import BaseCommand

from products.models import Category, Product
from purchases.models import Purchase
from sales.models import Sale


class Command(BaseCommand):
    help = "Exporte les données du magasin en CSV"

    def handle(self, *args, **options):

        export_dir = "exports"

        os.makedirs(export_dir, exist_ok=True)

        # =========================
        # CATEGORIES
        # =========================

        with open(
            f"{export_dir}/categories.csv",
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "id",
                "name",
            ])

            for category in Category.objects.all():
                writer.writerow([
                    category.id,
                    category.name,
                ])

        # =========================
        # PRODUCTS
        # =========================

        with open(
            f"{export_dir}/products.csv",
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "id",
                "sku",
                "name",
                "category_id",
                "purchase_price",
                "selling_price",
                "stock",
                "is_active",
            ])

            products = Product.objects.select_related("category")

            for product in products:
                writer.writerow([
                    product.id,
                    product.sku,
                    product.name,
                    product.category.id,
                    product.purchase_price,
                    product.selling_price,
                    product.stock,
                    product.is_active,
                ])

        # =========================
        # PURCHASES
        # =========================

        with open(
            f"{export_dir}/purchases.csv",
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "id",
                "supplier",
                "product_id",
                "quantity",
                "unit_price",
                "date",
                "total_cost",
            ])

            purchases = Purchase.objects.select_related("product")

            for purchase in purchases:

                total_cost = (
                    purchase.quantity *
                    purchase.unit_price
                )

                writer.writerow([
                    purchase.id,
                    purchase.supplier,
                    purchase.product.id,
                    purchase.quantity,
                    purchase.unit_price,
                    purchase.date,
                    total_cost,
                ])

        # =========================
        # SALES
        # =========================

        with open(
            f"{export_dir}/sales.csv",
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "id",
                "product_id",
                "quantity",
                "unit_price",
                "date",
                "revenue",
            ])

            sales = Sale.objects.select_related("product")

            for sale in sales:

                revenue = (
                    sale.quantity *
                    sale.unit_price
                )

                writer.writerow([
                    sale.id,
                    sale.product.id,
                    sale.quantity,
                    sale.unit_price,
                    sale.date,
                    revenue,
                ])

        self.stdout.write(
            self.style.SUCCESS(
                "Export terminé avec succès."
            )
        )