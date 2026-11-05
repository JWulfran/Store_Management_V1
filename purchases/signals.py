from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from products.models import Product
from .models import Purchase

@receiver(post_save, sender=Purchase)
def increase_product_stock(sender, instance, created, **kwargs):
    if created:
        Product.objects.filter(pk=instance.product_id).update(stock=F("stock")+ instance.quantity)