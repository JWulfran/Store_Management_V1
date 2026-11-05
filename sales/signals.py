from django.core.exceptions import ValidationError
from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from products.models import Product
from .models import Sale

@receiver(post_save, sender=Sale)
def decrease_product_stock(sender, instance, created, **kwargs):

    if not created:
        return

    updated = Product.objects.filter(pk=instance.product_id, stock__gte=instance.quantity,).update(stock=F("stock")- instance.quantity)

    if updated == 0:
        raise ValidationError("Stock insuffisant pour effectuer cette vente.")

@receiver(post_delete, sender=Sale)
def restore_product_stock(sender, instance, **kwargs):
    Product.objects.filter(pk=instance.product_id).update(stock=F("stock") + instance.quantity)

