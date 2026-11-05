from django import forms
from products.models import Product
from .models import Sale

class SalesForm(forms.ModelForm):

    class Meta:
        model = Sale
        fields = ['product','quantity', 'date']
        widgets = {
            'product': forms.Select(attrs={"class":"form-select",}),
            'quantity': forms.NumberInput(attrs={"class":"form-control", "min":1,}),
            'date': forms.DateInput(attrs={"class":"form-control","type":"date",}),
        }

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True, stock__gt=0).order_by("name")

    def clean(self):
        cleaned_data = super().clean()

        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")

        if product and quantity:
            if quantity > product.stock:
                self.add_error("quantity",f"Stock insuffisant. Stock disponible : {product.stock} ")
        return cleaned_data