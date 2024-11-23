from django.shortcuts import render,redirect
from shop.models import Product
from cart.models import Cart,Payment,Order_details
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login
import razorpay


# Create your views here.
@login_required
def addtocart(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(product=p,user=u)
        if(p.stock>0):
            c.quantity+=1
            c.save()
            p.stock-=1
            p.save()



    except:

        c=Cart.objects.create(product=p,user=u,quantity=1)
        if(p.stock>0):
            c.save()
            p.stock-=1
            p.save()

    return redirect('cart:cart')

@login_required
def cart_view(request):
    u=request.user
    # total=0

    c=Cart.objects.filter(user=u)
    total=0

    for i in c:
        total+=i.quantity*i.product.price



    context={'cart':c,'total':total}
    return render(request,"cart.html",context)

@login_required
def cart_remove(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)

        if(c.quantity > 1):
            c.quantity -=1
            c.save()
            p.stock+=1
            p.save()
        else:
            c.delete()
            p.stock +=1
            p.save()
    except:
        pass


    return redirect('cart:cart')
@login_required
def cart_delete(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    c=Cart.objects.get(user=u,product=p)
    c.delete()
    p.stock+=c.quantity
    p.save()



    return  redirect('cart:cart')



def order_form(request):
    if(request.method=="POST"):
        address=request.POST['a']
        phone=request.POST['p']
        pin=request.POST['pn']
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total+=i.quantity*i.product.price
        total1=int(total*100)
        # print(total)

        client=razorpay.Client(auth=('rzp_test_vp0N19PUI6nETX','LDln51UO9BTkxPztPdGLNSf1')) #creates a client connection

        response_payment=client.order.create(dict(amount=total1,currency="INR"))
        print(response_payment)

        order_id=response_payment['id']

        status=response_payment['status']

        if(status=="created"):

            p=Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c:
                o=Order_details.objects.create(product=i.product,user=u,no_of_items=i.quantity,address=address,phone_no=phone,pin=pin,order_id=order_id)
                o.save()
        response_payment['name']=u.username
        context={'payment':response_payment}
        return render(request,'payment.html',context)

    return render(request,'order_form.html')

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
            c=Cart.objects.filter(user=usr)
            c.delete()


        except:
            pass



    return render(request,'payment_status.html',{'status':status})











