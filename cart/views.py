from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from . import cart
from .cart import Cart


# Create your views here.
@login_required
@require_POST
def add_cart(request):
    try:
        artCd = request.POST.get('artCd')
        price=request.POST.get('price')
        image_url=request.POST.get('image_url')
        art_name = request.POST.get('art_name')

        cart = Cart(request)
        cart.add(artCd, price, image_url, art_name)
        return redirect('cart_detail')

    except Exception as e:
        print(f"카트 담기 오류: {e}")
        # 오류 처리 및 사용자에게 알림을 위한 로직 추가
        return HttpResponseBadRequest('카트 담기 중 오류가 발생했습니다.')

@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})

@require_POST
def cart_remove(request):
    artCd = request.POST.get('artCd')
    cart = Cart(request)
    cart.remove(artCd)
    return redirect('cart_detail')