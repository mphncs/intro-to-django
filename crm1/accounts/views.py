from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
# Create your views here.
from .models import *
from .forms import OrderForm


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


def create_order(request, primary_key):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    id_customer = Customer.objects.get(id=primary_key)
    # form = OrderForm(initial={'customer': id_customer})
    formset = OrderFormSet(queryset=Order.objects.none(), instance=id_customer)

    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=id_customer)
        if formset.is_valid():
            form.save()
            return redirect('/')

    context = {'formset': formset}

    return render(request, 'accounts/order_form.html', context=context)


def update_order(request, primary_key):
    id_order = Order.objects.get(id=primary_key)
    form = OrderForm(instance=id_order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=id_order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}

    return render(request, 'accounts/order_form.html', context=context)


def delete_order(request, primary_key):
    item = Order.objects.get(id=primary_key)

    if request.method == 'POST':
        item.delete()
        return redirect('/')

    context = {'item': item}

    return render(request, 'accounts/delete_order.html', context=context)
