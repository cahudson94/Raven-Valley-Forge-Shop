"""."""
from django.contrib import admin
from account.models import Account, ShippingInfo, Order, SlideShowImage

admin.site.register(Account)
admin.site.register(ShippingInfo)
admin.site.register(Order)
admin.site.register(SlideShowImage)
