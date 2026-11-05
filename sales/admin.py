from django.contrib import admin

from .models import Sale

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display=("product","quantity","unit_price","display_total","date",)
    list_filter=("date","product",)
    search_fields=("product__name",)
    ordering=("-date","-created_at",)

    @admin.display(description="Total")
    def display_total(self, obj):
        return obj.total