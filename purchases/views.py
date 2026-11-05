from django.shortcuts import render, redirect
from django.contrib import messages

from products.models import Product
from .forms import PurchaseForm
from .models import Purchase


def purchase_list(request):
    purchases = (Purchase.objects.select_related("product","product__category").all()) 
    context = {"purchases":purchases}
    return render(request, "purchases/purchase_list.html", context)


def purchase_create(request):
    products = Product.objects.filter(is_active=True).order_by("name")

    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save()
            messages.success(
                request, f"Achat de {purchase.quantity}"
                         f"{purchase.product.name} enregistré avec succès."
                            )
            return redirect("purchases:purchase_list")

    else:
        form = PurchaseForm()

    product_prices = {
        str(product.id): str(product.purchase_price)
        for product in products
    }

    context = {
        "form": form,
        "product_prices": product_prices,
    }

    return render(request, "purchases/purchase_form.html", context)
