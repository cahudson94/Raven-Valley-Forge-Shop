"""."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.account, name='account'),
]
