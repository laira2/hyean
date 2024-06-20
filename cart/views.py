from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from .models import Cart, CartAddedItem
from orders.models import OrderItem
from user_account.models import Profile

@login_required
@require_POST
def add_cart(request):
    try:
        user = request.user

        # 프로필이 존재하는지 확인
        if not hasattr(user, 'profile'):
            # 프로필 생성
            Profile.objects.create(user=user)

        # 사용자의 장바구니 가져오기 또는 생성하기
        cart, created = Cart.objects.get_or_create(user=user)

        artCd = request.POST.get('artCd')
        price = request.POST.get('price')
        image_url = request.POST.get('image_url')
        art_name = request.POST.get('art_name')

        # OrderItem에 존재하는지 확인
        if OrderItem.objects.filter(artCd=artCd).exists():
            return render(request, 'detail.html', {
                'is_sold_out': True,
            })

        # CartAddedItem에 존재하는지 확인
        if CartAddedItem.objects.filter(cart=cart, artCd=artCd).exists():
            return redirect('cart_detail')

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
    cart, created = Cart.objects.get_or_create(user=request.user)
    print(cart)
    cart_items = cart.cartaddeditem_set.all()
    if cart_items:
        print(cart_items)
        total_price = sum(item.price for item in cart_items)
        return render(request, 'cart/detail.html', {'cart_items': cart_items, 'total_price':total_price})
    else:
        error_message ="카트에 담긴 제품이 없습니다."
        return render(request, 'cart/detail.html', {'error_message':error_message})

@require_POST
def cart_remove(request):
    cart= get_object_or_404(Cart, user=request.user)
    artCd = request.POST.get('artCd')
    cart_item = CartAddedItem.objects.filter(cart=cart,artCd=artCd)
    cart_item.delete()
    return redirect('cart_detail')