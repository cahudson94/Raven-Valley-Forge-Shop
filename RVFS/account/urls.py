"""."""
from django.urls import path
from account.views import (AccountView,
                           InfoFormView,
                           EditAccountView,
                           AddAddressView,
                           AddressListView,
                           DeleteAddress)

urlpatterns = [
    path('', AccountView.as_view(), name='account'),
    path('add-address/', AddAddressView.as_view(), name='add_add'),
    path('address-list/', AddressListView.as_view(), name='add_list'),
    path('delete-address/<int:pk>/', DeleteAddress.as_view(), name='del_add'),
    path('edit/<int:pk>/', EditAccountView.as_view(), name='edit_acc'),
    path('info-form/<int:pk>/', InfoFormView.as_view(), name='info_reg')
]
