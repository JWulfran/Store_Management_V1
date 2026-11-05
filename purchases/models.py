from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils import timezone

from products.models import Product


class Purchase(models.Model):
    supplier = models.CharField(max_length=150)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchases')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10,decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateField(auto_now_add=True)

    class Meta :
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.product.name} -  {self.quantity}"

    @property
    def total(self):
        return self.quantity * self.unit_price

