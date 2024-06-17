# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from .forms import OrderForm
from .models import Order, OrderItem
from cart.models import Cart
from django.contrib.auth.decorators import login_required


@login_required
def order_page(request):
<<<<<<< Updated upstream
    cart = Cart(request)

    if not cart.cart:
        return redirect('cart:detail')

    if request.method == 'POST':
=======
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
>>>>>>> Stashed changes
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
<<<<<<< Updated upstream
            order.total_price = cart.get_total_price()
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product_name=item['art_name'],
                    quantity=item['quantity'],
                    price=item['price']
                )
            cart.clear()
            amount = order.total_price
            return redirect('payments:checkout_view', order_id=order.id, amount=amount)
    else:
        form = OrderForm()
    return render(request, 'order.html', {'cart': cart, 'form': form})
=======
            cart_items = cart.cartaddeditem_set.all()
            for item in cart_items:
                OrderItem.objects.create(order=order,
                                         artCd=item['artCd'],
                                         art_name=item['art_name'],
                                         price=item['price'],
                                         image_url=item['image_url'])
            order.save()
            return render(request, 'order.html', {'cart_items': cart_items, 'form': form})
    else:
        form = OrderForm()
    return render(request, 'order.html', {'form': form})
>>>>>>> Stashed changes


# 개같이 멸망!
def order_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            cart = Cart(request)
            for item in cart:
                OrderItem.objects.create(order=order,
                                         artCd=item['artCd'],
                                         art_name=item['art_name'],
                                         price=item['price'],
                                         image_url=item['image_url'])

            cart.clear()
            order.save()
            return render(request, 'pay', {'order': order})
        return HttpResponseBadRequest('잘못된 요청입니다.')
    else:
        form = OrderForm()
        cart = Cart(request)
    return render(request, 'order.html', {'form': form, 'cart': cart})
