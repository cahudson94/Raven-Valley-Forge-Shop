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
from account.views import (CustomReg, CustomLog, about, home)

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('login/', CustomLog.as_view(), name='login'),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    path('admin/', admin.site.urls),
    path('register', CustomReg.as_view(), name='register'),
    path('accounts/', include('registration.backends.hmac.urls')),
    path('account/', include('account.urls')),
    path('products/', include('products.urls')),
    path('services/', include('services.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
