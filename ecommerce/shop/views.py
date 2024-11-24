from django.shortcuts import render
from shop.models import Category, Product
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

def categories(request):
    c = Category.objects.all()
    context={'cat':c}
    return render(request, 'categories.html', {'categories': c})

def products(request,p):
    c=Category.objects.get(id=p)
    p=Product.objects.filter(category=c)
    context = {'cat':c,'product': p}
    return render(request,'products.html',context)  # Pass products to the template

def details(request,p):
    pro=Product.objects.get(id=p)
    context={'product':pro}
    return render(request,'detail.html',context)


def register(request):
    if request.method == "POST":
        u = request.POST['u']
        p = request.POST['p']
        cp = request.POST['cp']
        f = request.POST['f']
        l = request.POST['l']
        e = request.POST['e']

        # Check if the username already exists
        if User.objects.filter(username=u).exists():
            return HttpResponse("Username already exists. Please choose a different one.")

        # Check if passwords match
        if p == cp:
            user = User.objects.create_user(username=u, password=p, email=e, first_name=f, last_name=l)
            user.save()
            return redirect('shop:categories')
        else:
            return HttpResponse("Passwords do not match.")

    return render(request, 'register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            login(request, user)
            return redirect('shop:categories')  # Redirect to the desired page after login
        else:
            return HttpResponse("Invalid username or password.")

    return render(request, 'login.html')
