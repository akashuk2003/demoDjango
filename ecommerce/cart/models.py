from django.db import models

# Create your models here.
# cart/models.py
from django.contrib.auth.models import User
from shop.models import Product

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.quantity}"

def subtotal(self):
    return self.quantity*self.product.price

class Payment(models.Model):
    name=models.CharField(max_length=30)
    amount=models.IntegerField()
    order_id=models.CharField(max_length=30,blank=True)
    razorpay_payment_id=models.CharField(max_length=30,blank=True)
    paid=models.BooleanField(default=False)

class Order_details(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    no_of_items=models.IntegerField()
    address=models.CharField(max_length=30)
    phone=models.BigIntegerField()
    pin=models.IntegerField()
    order_id=models.CharField(max_length=30)
    ordered_date=models.DateTimeField(auto_now_add=True)
    payment_status=models.CharField(max_length=30,default="pending")
    delivery_status=models.CharField(max_length=30,default="pending")

