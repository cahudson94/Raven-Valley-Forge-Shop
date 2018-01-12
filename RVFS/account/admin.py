"""."""
from django.contrib import admin
from account.models import Account, ShippingInfo

admin.site.register(Account)
admin.site.register(ShippingInfo)
