from django.shortcuts import render, redirect
from django.http import Http404
from .forms import OrderForm
from .models import Order
import aiohttp
from artWork.views import cached_data, get_image_data

async def order_view(request, artCd):
    """주문 폼을 표시하고 처리하는 함수"""
    try:
        # 이미 캐시된 데이터에서 이미지 정보 가져오기
        images = cached_data['images'].get(artCd, {})
        if not images:
            raise Exception(f"Image data not found for artCd: {artCd}")

        art_name = images.get('art_name', '')
        file_name = images.get('file_name', '')
        price = images.get('price', 0)

        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                # 폼에서 artCd, art_name, file_name, price를 저장할 수 있도록 처리
                order = form.save(commit=False)
                order.artCd = artCd
                order.art_name = art_name
                order.file_name = file_name
                order.price = price
                order.save()
                return redirect('order_success')
        else:
            initial_data = {
                'artCd': artCd,
                'art_name': art_name,
                'file_name': file_name,
                'price': price,
            }
            form = OrderForm(initial=initial_data)

        context = {
            'form': form,
            'artCd': artCd,
            'art_name': art_name,
            'file_name': file_name,
            'price': price,
        }
        return render(request, 'order_form.html', context)
    except Exception as e:
        print(f"주문 페이지 렌더링 오류: {e}")
        return render(request, 'order_form.html', {'error_message': '주문 페이지를 로드하는 중 오류가 발생했습니다.'})
