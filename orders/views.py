# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
import os
from django.urls import reverse
from .forms import OrderForm
from django.utils import timezone
from .models import Order, OrderItem
from cart.models import Cart, CartAddedItem
from django.contrib.auth.decorators import login_required


@login_required
def order_page(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartaddeditem_set.all()
    cart_total_price = sum(item.price for item in cart_items)

    if request.method == 'POST':
        print("Total Price:", cart_total_price)
        form = OrderForm(request.POST)
        if form.is_valid():

            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart_total_price
            order.save()  # Save the order first to get the order ID


            timestamp_str = timezone.now().strftime("%Y%m%d%H%M%S")
            order_id = f"{timestamp_str}{order.user.id}"
            print("Total Price:", cart_total_price)

            for item in cart_items:
                print(item.art_name)
                OrderItem.objects.create(
                    order=order,
                    artCd=item.artCd,
                    art_name=item.art_name,
                    quantity=1,  # Ensure quantity is included if it exists
                    price=item.price,
                    image_url=item.image_url
                )

            context = {
                'order_id': order_id,
                'email': form.cleaned_data['email'],
                'name': form.cleaned_data['name'],
                'phone': form.cleaned_data['phone'],
                'total_price': cart_total_price,
                'toss_payments_client_key': ('test_gck_docs_Ovk5rk1EwkEbP0W43n07xlzm')
            }
            # Optionally, clear the cart after saving the order
            cart.cartaddeditem_set.all().delete()

            return redirect('payments:my_view', order_id=order_id)
    else:
        form = OrderForm()

    return render(request, 'order.html', {
        'order_form': form,
        'cart_items': cart_items,
        'total_price': cart_total_price
    })

