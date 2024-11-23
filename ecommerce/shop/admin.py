from django.contrib import admin

# Register your models here.
from shop.models import Categories
from shop.models import Product

admin.site.register(Categories)
admin.site.register(Product)