from django.urls import path

from . import views

app_name = "sales"

urlpatterns = [
    path('', views.sale_list, name='sales_list'),
    path('add/', views.sale_create, name='sale_create'),
]