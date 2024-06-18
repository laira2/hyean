# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderForm
from .models import Order, OrderItem
from cart.models import Cart, CartAddedItem
from django.contrib.auth.decorators import login_required


@login_required
def order_page(request):
    cart = get_object_or_404(Cart, user=request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.get_total_price()
            order.save()

            cart_items = CartAddedItem.objects.filter(cart=cart)
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    cart_item=cart_item,
                    quantity=1,
                    price=cart_item.price
                )

            cart_items.delete()

            return redirect('payments:checkout_view', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'order.html', {'cart': cart, 'form': form})


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
