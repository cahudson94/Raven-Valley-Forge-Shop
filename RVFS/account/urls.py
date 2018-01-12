"""."""
from django.urls import path
from account.views import AccountView, InfoFormView

urlpatterns = [
    path('', AccountView.as_view(), name='account'),
    path('info-form/<int:pk>/', InfoFormView.as_view(), name='info_reg')
]
