"""."""
from django.urls import path
from catalog.views import (CreateProductView as CreateProd,
                           EditProductView as EditProd,
                           SingleProductView as Prod,
                           CatalogueView as Cat,
                           CreateServiceView as CreateServ,
                           EditServiceView as EditServ,
                           SingleServiceView as Serv,
                           ServiceInfoView as ServInfo,
                           CheckoutCompleteView as CheckComp,
                           CartView,
                           CheckoutView,
                           AllItemsView,
                           )
from catalog import views

urlpatterns = [
    path('list/', AllItemsView.as_view(), name='list'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/update_cart/', views.update_cart, name='update_cart'),
    path('cart/delete_item/', views.delete_item, name='delete_item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('create-payment/', views.create_payment, name='create_payment'),
    path('checkout-complete/', CheckComp.as_view(), name='check_comp'),
    path('add-product/', CreateProd.as_view(), name='add_prod'),
    path('edit-product/<int:pk>/', EditProd.as_view(), name='edit_prod'),
    path('products/<int:pk>/', Prod.as_view(), name='prod'),
    path('products/', Cat.as_view(), name='prods'),
    path('products/<slug:slug>/', Cat.as_view(), name='tagged_products'),
    path('add-service/', CreateServ.as_view(), name='add_serv'),
    path('edit-service/<int:pk>/', EditServ.as_view(), name='edit_serv'),
    path('services/<int:pk>/', Serv.as_view(), name='serv'),
    path('services/info/<int:pk>/', ServInfo.as_view(), name='serv_info'),
    path('services/', Cat.as_view(), name='servs'),
    path('services/<slug:slug>/', Cat.as_view(), name='tagged_services'),
]
