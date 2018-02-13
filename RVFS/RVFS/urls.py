"""RVFS URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from account.views import (CustomRegView,
                           CustomLogView,
                           AboutView,
                           HomeView,
                           GalleryView,
                           OrdersView,
                           OrderView
                           )
from account import views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('update/', views.updateslideshow, name='update'),
    path('about/', AboutView.as_view(), name='about'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderView.as_view(), name='order'),
    path('gallery/<slug:slug>/', GalleryView.as_view(), name='gallery'),
    path('login/', CustomLogView.as_view(), name='login'),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    path('admin/', admin.site.urls),
    path('register/', CustomRegView.as_view(), name='register'),
    path('accounts/', include('registration.backends.hmac.urls')),
    path('account/', include('account.urls')),
    path('shop/', include('catalog.urls')),
    path('', include('sendemail.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
