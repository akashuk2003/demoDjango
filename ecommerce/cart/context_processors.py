


from cart.models import CartItem

def count_items(request):
    u = request.user
    count = 0
    if request.user.is_authenticated:
        try:
            cart_items = CartItem.objects.filter(user=u)
            for item in cart_items:
                count += item.quantity
        except CartItem.DoesNotExist:
            count = 0
    return {'count_items': count}

