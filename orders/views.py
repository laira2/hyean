from django.shortcuts import render, redirect
from django.http import Http404
from .forms import OrderForm
from .models import Order
import aiohttp
from artWork.views import cached_data, get_image_data
from cart import Cart


async def order_view(request):
    """주문 폼을 표시하고 처리하는 함수"""
    cart = Cart(request)
    cart_items = cart.get_cart_items()
    user = request.user

    try:
        # 장바구니 데이터 사용하기
        for item in cart_items:
            artCd = item['artCd']
            art_name = item['art_name']
            quantity = item['quantity']
            price = item['price']
            image_url = item['image_url']
            # 주문 처리 로직

            cart.clear()

        return render(request, 'order.html', {'cart_items': cart_items, 'user': user})
    except Exception as e:
        print(f"주문 페이지 렌더링 오류: {e}")
        return render(request, 'order.html', {'error_message': '주문 페이지를 로드하는 중 오류가 발생했습니다.'})
