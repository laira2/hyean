# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderForm
from django.utils import timezone
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
        print("OrderForm 잘 되는지 확인")
        if form.is_valid():

            order = form.save(commit=False)
            order.user = request.user
            order.save()  # Save the order first to get the order ID

            # Generate unique order_id
            timestamp_str = timezone.now().strftime("%Y%m%d%H%M%S")
            order_id = f"ORD-{timestamp_str}-{order.user.id}"

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    artCd=item.artCd,
                    art_name=item.art_name,
                    quantity=1,  # Ensure quantity is included if it exists
                    price=item.price,
                    image_url=item.image_url
                )

            # Optionally, clear the cart after saving the order
            cart.cartaddeditem_set.all().delete()

            return redirect('payments:my_view', order_id=order_id)
    else:
        form = OrderForm()

    return render(request, 'order.html', {
        'order_form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })

