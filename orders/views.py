# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from .forms import OrderForm
from .models import Order, OrderItem
from cart.models import Cart
from django.contrib.auth.decorators import login_required


@login_required
def order_page(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartaddeditem_set.all()
    total_price = sum(item.price for item in cart_items)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            for item in cart_items:
                OrderItem.objects.create(order=order,
                                         artCd=item['artCd'],
                                         art_name=item['art_name'],
                                         price=item['price'],
                                         image_url=item['image_url'])
            print(order)
            order.save()
            return render(request, 'order.html')
    else:
        form = OrderForm()
    return render(request, 'order.html', {'order_form': form,'cart_items':cart_items,'total_price':total_price})

