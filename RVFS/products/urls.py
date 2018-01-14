"""."""
from django.urls import path

from products.views import CreateProductView

urlpatterns = [
    path('add-product/', CreateProductView.as_view(), name='add_prod'),
]
