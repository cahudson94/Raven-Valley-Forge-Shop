"""."""
from django.urls import path
from catalog.views import (CreateProductView as CreateProd,
                           EditProductView as EditProd,
                           SingleProductView as Prod,
                           AllProductsView as Prods,
                           TagProductsView as TagProds,
                           CreateServiceView as CreateServ,
                           EditServiceView as EditServ,
                           SingleServiceView as Serv,
                           AllServicesView as Servs,
                           TagServicesView as TagServs,
                           )

urlpatterns = [
    path('add-product/', CreateProd.as_view(), name='add_prod'),
    path('edit-product/<int:pk>/', EditProd.as_view(), name='edit_prod'),
    path('products/<int:pk>/', Prod.as_view(), name='prod'),
    path('products/', Prods.as_view(), name='prods'),
    path('products/<slug:slug>/', TagProds.as_view(), name='tagged_products'),
    path('add-service/', CreateServ.as_view(), name='add_serv'),
    path('edit-service/<int:pk>/', EditServ.as_view(), name='edit_serv'),
    path('services/<int:pk>/', Serv.as_view(), name='serv'),
    path('services/', Servs.as_view(), name='servs'),
    path('services/<slug:slug>/', TagServs.as_view(), name='tagged_services'),
]
