from django.shortcuts import render, get_object_or_404, redirect
from shop.models import Product
from cart.models import CartItem
from cart.models import Payment,Order_details
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.contrib.auth import login
from django.http import HttpResponse
from collections import defaultdict
@login_required
def addtocart(request, i):
    # Retrieve the product based on the provided ID
    p = get_object_or_404(Product, id=i)
    u = request.user  # Use request.user directly, without parentheses

    # Create a CartItem for the current user and selected product
    cart_item, created = CartItem.objects.get_or_create(
        product=p,
        user=u,
        defaults={'quantity': 1}
    )
    try:
        c=CartItem.objects.get(product=p,user=u)
        c.quantity+=1
        c.save()
    except:
        c=CartItem.objects.get(product=p,user=u,quantity=1)
        c.save()

    # Add a success message for feedback
    messages.success(request, f"{p.name} has been added to your cart.")

    # Redirect to a cart view page or another relevant page
    return redirect('cart:cart')  # Ensure 'cart:view_cart' exists in your URLs


def cart_view(request):
    u = request.user
    cart_items = CartItem.objects.filter(user=u)

    total_price = 0
    for item in cart_items:
        item.subtotal = item.quantity * item.product.price
    total_price = sum(item.subtotal for item in cart_items)

    context = {'cart': cart_items, 'total_price': total_price}
    return render(request, 'cart.html', context)


@login_required
def remove_cart(request, r):
    cart_item = get_object_or_404(CartItem, id=r, user=request.user)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    # Redirect back to the cart page
    return redirect('cart:cart')

@login_required
def delete_cart(request,d):
    cart_item=get_object_or_404(CartItem,id=d,user=request.user)
    cart_item.delete()

    return redirect('cart:cart')



def order_form(request):
    if request.method == "POST":
        # Retrieve POST data and validate
        address = request.POST.get('a')
        phone = request.POST.get('p')
        pin = request.POST.get('pn')

        if not all([address, phone, pin]):  # Check if all fields are filled
            messages.error(request, "Please fill in all required fields.")
            return redirect('cart:order_form')  # Redirect to the order form page

        u = request.user
        c = CartItem.objects.filter(user=u)

        # Calculate the total price
        total = sum(i.quantity * i.product.price for i in c)
        total1 = int(total * 100)  # Convert to paise (Razorpay expects amount in paise)

        # Razorpay client setup
        client = razorpay.Client(auth=('rzp_test_vp0N19PUI6nETX', 'LDln51UO9BTkxPztPdGLNSf1'))
        response_payment = client.order.create(dict(amount=total1, currency="INR"))

        # Extract payment details
        order_id = response_payment['id']
        status = response_payment['status']

        if status == "created":
            # Save payment and order details
            p = Payment.objects.create(name=u.username, amount=total, order_id=order_id)
            for i in c:
                Order_details.objects.create(
                    product=i.product, user=u, no_of_items=i.quantity,
                    address=address, phone=phone, pin=pin, order_id=order_id
                )

            # Adding username to the payment response
            response_payment['name'] = u.username
            context = {'payment': response_payment}
            return render(request, 'payment.html', context)

    return render(request, 'order.html')  # Render the order form if not POST



@csrf_exempt
def payment_status(request,u):
    usr = User.objects.get(username=u)
    if not request.user.is_authenticated:
        login(request,usr)
    if(request.method=="POST"):
        response=request.POST
        print(response)

        param_dict={
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_payment_id':response['razorpay_payment_id'],
            'razorpay_signature':response['razorpay_signature']


        }
        #to check authenticity of signature
        client = razorpay.Client(auth=('rzp_test_vp0N19PUI6nETX', 'LDln51UO9BTkxPztPdGLNSf1'))
        print(client)
        try:
            status=client.utility.verify_payment_signature(param_dict)
            print(status)

        #r
            p=Payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id=response['razorpay_payment_id']
            p.paid=True
            p.save()
        #
            o=Order_details.objects.filter(order_id=response['razorpay_order_id'])
            for i in o:
                i.payment_status="completed"
                i.save()
            usr=User.objects.get(username=u)
            c=CartItem.objects.filter(user=usr)
            c.delete()


        except:
            pass



    return render(request,'payment_status.html',{'status':status})



from collections import defaultdict

def your_orders(request):
    u = request.user  # Get the current logged-in user
    orders = Order_details.objects.filter(user=u)  # Get orders for the logged-in user

    # Group products by ID and calculate the total quantity
    grouped_orders = defaultdict(lambda: {'quantity': 0, 'order_date': None, 'status': None})

    for order in orders:
        product_id = order.product.id
        grouped_orders[product_id]['product'] = order.product
        grouped_orders[product_id]['quantity'] += order.no_of_items
        grouped_orders[product_id]['status'] = order.payment_status  # Assuming this is the field for order status

    # Convert grouped_orders to a list of dictionaries for easy template rendering
    context = {'grouped_orders': grouped_orders.values()}
    return render(request, 'your_orders.html', context)
