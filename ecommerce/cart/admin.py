from django.contrib import admin

# Register your models here.
from cart.models import CartItem
from cart.models import Payment,Order_details
admin.site.register(CartItem)
admin.site.register(Payment)
admin.site.register(Order_details)