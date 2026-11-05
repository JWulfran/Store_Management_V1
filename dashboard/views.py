from datetime import date
from decimal import Decimal

from django.db.models import (
    Sum,
    F,
    Count,
    DecimalField,
    ExpressionWrapper,
)
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from products.models import Product
from purchases.models import Purchase
from sales.models import Sale


MONEY_FIELD = DecimalField(
    max_digits=18,
    decimal_places=2
)


def transaction_amount():
    """
    Expression SQL : quantity * unit_price.
    Utilisable pour les achats et les ventes.
    """
    return ExpressionWrapper(
        F("quantity") * F("unit_price"),
        output_field=MONEY_FIELD,
    )


def last_six_months():
    """Retourne les six derniers mois, mois courant inclus."""

    today = timezone.localdate()

    months = []

    for offset in range(5, -1, -1):
        year = today.year
        month = today.month - offset

        while month <= 0:
            month += 12
            year -= 1

        months.append(date(year, month, 1))

    return months


def monthly_totals(model):
    """Calcule les montants mensuels des transactions."""

    months = last_six_months()

    results = (
        model.objects
        .filter(date__gte=months[0])
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum(transaction_amount()))
        .order_by("month")
    )

    totals = {
        row["month"].strftime("%Y-%m"): float(row["total"])
        for row in results
    }

    return [
        totals.get(month.strftime("%Y-%m"), 0)
        for month in months
    ]


def dashboard(request):

    # =========================================
    # 1. SALES KPIs
    # =========================================

    sales_stats = Sale.objects.aggregate(
        revenue=Sum(transaction_amount()),
        quantity_sold=Sum("quantity"),
        total_transactions=Count("id"),
    )

    total_revenue = (
        sales_stats["revenue"] or Decimal("0.00")
    )

    quantity_sold = sales_stats["quantity_sold"] or 0

    total_sales = sales_stats["total_transactions"]


    # =========================================
    # 2. PURCHASE KPIs
    # =========================================

    purchases_stats = Purchase.objects.aggregate(
        amount=Sum(transaction_amount()),
        quantity_purchased=Sum("quantity"),
    )

    total_purchases = (
        purchases_stats["amount"] or Decimal("0.00")
    )

    quantity_purchased = (
        purchases_stats["quantity_purchased"] or 0
    )


    # =========================================
    # 3. PRODUCT KPIs
    # =========================================

    products = Product.objects.filter(is_active=True)

    total_products = products.count()

    low_stock_products = products.filter(
        stock__lte=10
    ).count()

    out_of_stock_products = products.filter(
        stock=0
    ).count()


    # =========================================
    # 4. INVENTORY VALUE
    # =========================================

    inventory_expression = ExpressionWrapper(
        F("stock") * F("purchase_price"),
        output_field=MONEY_FIELD,
    )

    inventory_value = (
        Product.objects.aggregate(
            total=Sum(inventory_expression)
        )["total"] or Decimal("0.00")
    )


    # =========================================
    # 5. MONTHLY CHARTS
    # =========================================

    months = last_six_months()

    month_labels = [
        month.strftime("%Y-%m")
        for month in months
    ]

    monthly_sales = monthly_totals(Sale)

    monthly_purchases = monthly_totals(Purchase)


    # =========================================
    # 6. TOP SELLING PRODUCTS
    # =========================================

    top_products = (
        Sale.objects
        .values(
            "product__name",
            "product__sku"
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_revenue=Sum(transaction_amount()),
        )
        .order_by("-total_quantity")[:5]
    )


    # =========================================
    # 7. RECENT TRANSACTIONS
    # =========================================

    recent_sales = (
        Sale.objects
        .select_related("product")
        .order_by("-date", "-created_at")[:5]
    )

    recent_purchases = (
        Purchase.objects
        .select_related("product")
        .order_by("-date", "-created_at")[:5]
    )


    # =========================================
    # 8. CONTEXT
    # =========================================

    context = {
        "total_revenue": total_revenue,
        "total_purchases": total_purchases,
        "quantity_sold": quantity_sold,
        "quantity_purchased": quantity_purchased,
        "total_sales": total_sales,
        "total_products": total_products,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
        "inventory_value": inventory_value,

        "month_labels": month_labels,
        "monthly_sales": monthly_sales,
        "monthly_purchases": monthly_purchases,

        "top_products": top_products,
        "recent_sales": recent_sales,
        "recent_purchases": recent_purchases,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )