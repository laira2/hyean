# detail_page.py

from django.shortcuts import render
import aiohttp
from .views import cached_data, get_image_data  # 필요한 모듈 임포트

async def detail_view(request, artCd):
    """상세 페이지를 렌더링하는 함수"""
    try:
        # 이미 캐시된 데이터에서 이미지 정보 가져오기
        images = cached_data['images'].get(artCd, {})
        print(f"이미지 데이터: {images}")
        if not images:
            raise Exception(f"Image data not found for artCd: {artCd}")

        file_url = images.get('file_url', '')
        price = images.get('price', 0)

        # 이미지 데이터 확인을 위한 프린트문 추가
        print(f"file_url: {file_url}, artCd: {artCd}, price: {price}")

        # 이미지와 관련된 메타 정보 가져오기
        file_url = images.get('file_url', '')
        file_name = images.get('file_name', '')
        art_name = images.get('art_name', '')
        art_width = images.get('art_width', '')
        art_vrticl = images.get('art_vrticl', '')
        price = images.get('price', '')

        context = {
            'art_name': art_name,
            'file_url': file_url,
            'file_name': file_name,
            'art_info': {
                'artCd': artCd,
            },
            'art_dimensions': {
                'art_width': art_width,
                'art_vrticl': art_vrticl,
            },
            'price': price
        }
        print(f"데이터 전체 항목: {context}")  # 확인을 위한 출력
        return render(request, 'detail.html', context)

    except Exception as e:
        print(f"상세 페이지 렌더링 오류: {e}")  # 에러 메시지 출력
        return render(request, 'detail.html', {'error_message': '상세 페이지를 불러오는 중 오류가 발생했습니다.'})

