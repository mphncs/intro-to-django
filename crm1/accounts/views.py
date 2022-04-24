from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
# Create your views here.
from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_user, admin_only


@unauthenticated_user
def signup_page(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(user=user)

            messages.success(request, f'Account {username} was created')
            return redirect('login')

    context = {'form': form}

    return render(request, 'accounts/signup.html', context=context)


@unauthenticated_user
def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username or password is incorrect')

    context = {}

    return render(request, 'accounts/login.html', context=context)


def logout_page(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()

    total_orders = orders.count()
    num_orders_pending = orders.filter(status='Pending').count()
    num_orders_delivered = orders.filter(status='Delivered').count()

    context = {
        'orders': orders,
        'customers': customers,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'num_orders_pending': num_orders_pending,
        'num_orders_delivered': num_orders_delivered
    }

    return render(request, 'accounts/dashboard.html', context=context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def user_page(request):
    orders = request.user.customer.order_set.all()

    total_orders = orders.count()
    num_orders_pending = orders.filter(status='Pending').count()
    num_orders_delivered = orders.filter(status='Delivered').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'num_orders_pending': num_orders_pending,
        'num_orders_delivered': num_orders_delivered
    }

    return render(request, 'accounts/user.html', context=context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def products(request):
    products_list = Product.objects.all()
    return render(request, 'accounts/products.html', {'products_list': products_list})


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def customer(request, primary_key):
    id_customer = Customer.objects.get(id=primary_key)
    orders = id_customer.order_set.all()
    num_orders = orders.count()

    my_filter = OrderFilter(request.GET, queryset=orders)
    orders = my_filter.qs

    context = {'id_customer': id_customer, 'orders': orders, 'num_orders': num_orders, 'my_filter': my_filter}

    return render(request, 'accounts/customer.html', context=context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def create_order(request, primary_key):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    id_customer = Customer.objects.get(id=primary_key)
    # form = OrderForm(initial={'customer': id_customer})
    formset = OrderFormSet(queryset=Order.objects.none(), instance=id_customer)

    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=id_customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'formset': formset}

    return render(request, 'accounts/order_form.html', context=context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def update_order(request, primary_key):
    id_order = Order.objects.get(id=primary_key)
    formset = OrderForm(instance=id_order)

    if request.method == 'POST':
        formset = OrderForm(request.POST, instance=id_order)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'formset': formset}

    return render(request, 'accounts/order_form.html', context=context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def delete_order(request, primary_key):
    item = Order.objects.get(id=primary_key)

    if request.method == 'POST':
        item.delete()
        return redirect('/')

    context = {'item': item}

    return render(request, 'accounts/delete_order.html', context=context)
