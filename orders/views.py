# orders/views.py
from django.shortcuts import render, redirect
from django.http import Http404
from .forms import OrderForm
from .models import Order
import aiohttp
from artWork.views import cached_data, get_image_data

def order_view(request):
    """주문 페이지를 렌더링하고 주문을 생성하는 함수"""
    cart = Cart(request)
    cart_items = cart.get_cart_items()  # 장바구니 데이터 받아올 준비
    user = request.user  # 로그인 되어있는 유저 데이터 읽기

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user  # 사용자 정보 추가
                    order.total_amount = sum(item['price'] * item['quantity'] for item in cart)
                    order.payment_status = 'pending'
                    order.save()

                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            art_code=item['artCd'],
                            art_name=item['art_name'],
                            quantity=item['quantity'],
                            price=item['price'],
                            image_url=item['image_url']
                        )

                    cart.clear()  # 장바구니 비우기
                    return render(request, 'orders/created.html', {'order': order})

            except Exception as e:
                logger.error(f"주문 처리 중 오류 발생: {e}")
                return render(request, 'orders/create.html', {'cart': cart, 'form': form, 'error_message': '주문 처리 중 오류가 발생했습니다.'})
    else:
        form = OrderCreateForm()

    return render(request, 'orders/create.html', {'cart': cart, 'form': form})