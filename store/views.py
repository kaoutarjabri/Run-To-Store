from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
import json
from .models import *
from .forms import *
from .filters import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'account was created for ' + user)
                return redirect('login')
    context = {'form':form}
    return render(request, 'store/signup.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('store')
            else:
                messages.info(request, 'wrong password')
                
    context = {}
    return render(request, 'store/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

def home(request):
    context = {}
    return render(request, 'store/home.html', context)

def profile(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':     
        form = CustomerForm(request.POST,request.FILES,instance=customer)
        if form.is_valid():
            form.save()


    context = {'form': form}
    return render(request, 'store/profile.html', context)

def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitems_set.all() #setting the child value (orderitem(class)) from the parent value(order(class)(FK))
        cartItems = order.get_cart_items
        # wishedItems = WishedItems.objects.count()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    if selected_category:
        products = Product.objects.filter(category__name=selected_category)
    else:
        products = Product.objects.all()
    myfilter = OrderFilter(request.GET, queryset = products)
    products = myfilter.qs
    context={'products': products, 'cartItems':cartItems, 'myfilter':myfilter, 'categories': categories}
    return render(request, 'store/store.html', context)

def productview(request, pk):
    # customer = request.user.customer
    product = Product.objects.get(id=pk)
    # order , created = Order.objects.get_or_create(customer=customer, complete=False)
    # cartItems = order.get_cart_items
# 'cartItems':cartItems
    context = {'product': product, }
    return render(request, 'store/product.html', context)

def createProduct(request):
    form = productForm(None)

    if request.method == 'POST':
        form = productForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('store')

    context={'form': form}
    return render(request, 'store/add_product.html', context)


def cart(request): 
    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitems_set.all() #setting the child value (orderitem(class)) from the parent value(order(class)(FK))
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items':0, 'shipping':False}
    context={'items': items,'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitems_set.all() #setting the child value (orderitem(class)) from the parent value(order(class)(FK))
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items':0, 'shipping':False}
    context={'items': items,'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context) 

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId :',productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer= customer, complete=False)

    orderItem, created = OrderItems.objects.get_or_create(order= order, product= product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity +1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity -1)
    elif action == 'delete':
        orderItem.quantity = 0

    orderItem.save()

    if orderItem.quantity <= 0 :
        orderItem.delete()
    
    return JsonResponse('item was added', safe=False)



def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = request.user.customer

    try:
        wishlist = customer.wishlist
    except Wishlist.DoesNotExist:
        wishlist = Wishlist.objects.create(customer=customer)

    wished_item, created = WishedItems.objects.get_or_create(
        product=product,
        wishlist=wishlist
    )
    return redirect('wish')
    # product = get_object_or_404(Product, id=product_id)
    # wishlist, created = Wishlist.objects.get_or_create(customer=request.user.customer)
    # wished_item, wished_item_created = WishedItems.objects.get_or_create(wishlist=wishlist, product=product)

    # if created or wished_item_created:
    #     # If the wishlist or wished item was just created, save it to the database
    #     wishlist.save()
    #     wished_item.save()

    # return redirect('store')  # Redirect the user to the wishlist page

@login_required
def wishlist(request):

    customer = request.user.customer
    wish_list, created = Wishlist.objects.get_or_create(customer = customer)
    wishlist_items = WishedItems.objects.all()


        
    order , created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitems_set.all() #setting the child value (orderitem(class)) from the parent value(order(class)(FK))
    cartItems = order.get_cart_items

    context = {
        'wishlist_items': wishlist_items,
        'wish_list':wish_list,
        'cartItems': cartItems
    }
    return render(request, 'store/wishlist.html', context)
    
    
    # data = json.loads(request.body)
        
    #     # productId = data['productId']
    #     # action = data['action']
    #     # if action == 'delete':
    #     #     wishlist_items.delete()
