from django.shortcuts import render
# Create your views here.
from .models import *


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


def products(request):
    products_list = Product.objects.all()
    return render(request, 'accounts/products.html', {'products_list': products_list})


def customer(request, primary_key):
    id_customer = Customer.objects.get(id=primary_key)
    orders = id_customer.order_set.all()
    num_orders = orders.count()

    context = {'id_customer': id_customer, 'orders': orders, 'num_orders': num_orders}

    return render(request, 'accounts/customer.html', context=context)
