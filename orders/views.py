# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderForm
from .models import Order, OrderItem
from cart.models import Cart, CartAddedItem
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
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    artCd=item.artCd,
                    art_name=item.art_name,
                    quantity=item.quantity,  # Ensure quantity is included if it exists
                    price=item.price,
                    image_url=item.image_url
                )

            # Optionally, clear the cart after saving the order
            cart.cartaddeditem_set.all().delete()

            return redirect('payments:my_view', order_id=order.id)
    else:
        form = OrderForm()

    return render(request, 'order.html', {
        'order_form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })

