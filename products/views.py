from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.select_related("category").all()

    context = {"products":products}

    return render(request, "products/product_list.html", context)
