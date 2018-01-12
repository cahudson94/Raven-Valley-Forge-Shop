"""."""
from django.urls import path

from services.views import CreateServiceView

urlpatterns = [
    path('add-service/', CreateServiceView.as_view(), name='add_serv'),
]
