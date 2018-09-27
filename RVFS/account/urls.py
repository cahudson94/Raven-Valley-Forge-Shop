"""."""
from django.urls import path, reverse_lazy
from account.views import (AccountView,
                           InfoFormView,
                           EditAccountView,
                           AddAddressView,
                           AddressListView,
                           DeleteAddress)
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', AccountView.as_view(), name='account'),
    path('add-address/', AddAddressView.as_view(), name='add_add'),
    path('address-list/', AddressListView.as_view(), name='add_list'),
    path('delete-address/<int:pk>/', DeleteAddress.as_view(), name='del_add'),
    path('edit/<int:pk>/', EditAccountView.as_view(), name='edit_acc'),
    path('info-form/<int:pk>/', InfoFormView.as_view(), name='info_reg'),
    path('change_password/', auth_views.PasswordChangeView.as_view(
         template_name='password_reset/change_password.html',
         success_url=reverse_lazy('change_password_done')),
         name='change_password'),
    path('change_password_done/', auth_views.PasswordChangeDoneView.as_view(
         template_name='password_reset/change_password_done.html',
         ),
         name='change_password_done')
]
