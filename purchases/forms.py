from django import forms
from .models import Purchase

class PurchaseForm(forms.ModelForm):

    class Meta :
        model = Purchase

        fields = ['supplier', 'product', 'quantity', 'unit_price', 'date']
        widgets = {
            "supplier": forms.TextInput(attrs={
                "class":"form-control",
                "placeholder": "Nom du fournisseur",
            }),
            "product":forms.Select(attrs={
                "class": "form-select",
            }),
            "quantity": forms.NumberInput(attrs={
                    "class":'form-control',
                    "min": 1,
            }),
            "unit_price": forms.NumberInput(attrs={
                "class":"form-control",
                "min": 1,
                "step": "0.01",
            }),
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
        }