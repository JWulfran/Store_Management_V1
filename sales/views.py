from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect

from products.models import Product

from .forms import SalesForm
from .models import Sale

def sale_list(request):

    sales = Sale.objects.select_related("product").all()

    return render(request, "sales/sales_list.html", {"sales":sales,})

def sale_create(request):
    if request.method == "POST":
        form = SalesForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                product = Product.objects.select_for_update().get(pk=form.cleaned_data["product"].pk)
                quantity = form.cleaned_data["quantity"]

                if quantity > product.stock:
                    form.add_error("quantity", f"Stock Insuffisant. Stock disponible : {product.stock}")
                else:
                    sale = form.save(commit=False)
                    sale.product = product
                    sale.unit_price = product.selling_price
                    sale.save()

                    messages.success(request, f"Vente de {sale.product.name} enregistrée avec succès.")

                    return redirect("sales:sales_list") 
    else:
        form = SalesForm()

    product_data = {
        str(product.id):{
            "price": str(product.selling_price),
            "stock": product.stock
        }

    for product in form.fields["product"].queryset

    }

    return render(request,"sales/sale_form.html", {"form":form, "product_data":product_data,})
