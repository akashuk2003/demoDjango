"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# cart/urls.py
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('addtocart/<int:i>/', views.addtocart, name='addtocart'),
    path('cart',views.cart_view,name="cart"),
    path('remove/<int:r>/',views.remove_cart, name='remove_cart'),
    path('delete/<int:d>/',views.delete_cart,name="delete_cart"),
    path('order_form/',views.order_form,name="order_form"),
    path('status/<u>', views.payment_status, name="status"),
    path('your_orders/',views.your_orders,name='your_orders'),
]
