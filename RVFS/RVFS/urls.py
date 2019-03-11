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
from django.urls import include, path, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from account.views import (CustomRegView,
                           CustomLogView,
                           AboutView,
                           HomeView,
                           GalleriesView,
                           GalleryView,
                           OrdersView,
                           OrderView,
                           PreOrderView,
                           ContactView,
                           UsersView,
                           CommentView,
                           NewsletterUnsubView,
                           NewsletterMobileView,
                           AppointmentMobileView,
                           DiscountsView,
                           )
from account import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('update-slides/', views.update_slideshow_view,
         name='update-slides'),
    path('update-mailing/', views.update_mailing_list_view,
         name='update-mailing'),
    path('newsletter-mobile/', NewsletterMobileView.as_view(),
         name='newsletter-mobile'),
    path('appointment-mobile/', AppointmentMobileView.as_view(),
         name='appointment-mobile'),
    path('discounts/', DiscountsView.as_view(), name='discounts'),
    path('discounts/update/', views.update_discount, name='update_discount'),
    path('users/', UsersView.as_view(), name='users'),
    path('users/<int:pk>/comment/', CommentView.as_view(), name='comment'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderView.as_view(), name='order'),
    path('preorders/<int:pk>/', PreOrderView.as_view(), name='pre_order'),
    path('galleries/', GalleriesView.as_view(), name='galleries'),
    path('gallery/<slug:slug>/', GalleryView.as_view(), name='gallery'),
    path('login/', CustomLogView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'), name='logout'),
    path('newsletter/', views.newsletter, name='newsletter'),
    path('newsletter/unsub/<path:path>/', NewsletterUnsubView.as_view(),
         name='newsletter_unsub'),
    path('admin/', admin.site.urls),
    path('register/', CustomRegView.as_view(), name='register'),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('account/', include('account.urls')),
    path('shop/', include('catalog.urls')),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset/password_reset_form.html',
             email_template_name='password_reset/password_reset_email.html',
             subject_template_name='password_reset/password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_done'),
         ),
         name='password_reset'),
    path('password_reset_sent/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password_reset_confirmation/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset/password_reset_confirm.html',
         ),
         name='password_reset_confirm'),
    path('password_reset_complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset/password_reset_complete.html',
         ),
         name='password_reset_complete'),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += [
        path('404/', TemplateView.as_view(template_name='404.html')),
        path('403/', TemplateView.as_view(template_name='403.html')),
        path('500/', TemplateView.as_view(template_name='500.html')),
    ]
