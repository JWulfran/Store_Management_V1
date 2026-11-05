from django.urls import path
from . import views

app_name = "purchases"

urlpatterns = [
    path("", views.purchase_list, name="purchase_list"),
    path("add/",views.purchase_create, name="purchase_create"),
]