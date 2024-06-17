from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from .models import Cart, CartAddedItem

@login_required
@require_POST
def add_cart(request):
    try:
        user = request.user

        # 사용자의 장바구니 가져오기 또는 생성하기
        cart, created = Cart.objects.get_or_create(user=user)

        artCd = request.POST.get('artCd')
        price = request.POST.get('price')
        image_url = request.POST.get('image_url')
        art_name = request.POST.get('art_name')

        # 장바구니에 항목 추가
        added_item = CartAddedItem.objects.create(
            cart=cart,
            artCd=artCd,
            art_name=art_name,
            price=price,
            image_url=image_url
        )
        return redirect('cart_detail')

    except Exception as e:
        print(f"카트 담기 오류: {e}")
        # 오류 처리 및 사용자에게 알림을 위한 로직 추가
        return HttpResponseBadRequest('카트 담기 중 오류가 발생했습니다.')
@login_required
def cart_detail(request):
    user = request.user
    cart =Cart.objects.get(user=user)
    cart_items = cart.cartaddeditem_set.all()
    return render(request, 'cart/detail.html', {'cart_items': cart_items})

@require_POST
def cart_remove(request):
    artCd = request.POST.get('artCd')
    cart_item = CartAddedItem.objects.filter(artCd=artCd)
    cart_item.delete()
    return redirect('cart_detail')