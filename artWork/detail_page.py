from django.shortcuts import render, get_object_or_404
from .views import cached_data  # artWork/views.py 캐시 데이터 사용
from cart.models import Cart


async def images(request, artCd):
    """캐시된 이미지 데이터 가져오기"""
    # request 매개변수는 사용하지 않지만, view 함수로 인식하기 위해 입력
    try:
        images = cached_data['images'].get(artCd, {})
        if not images:
            raise Exception(f"Image data not found for artCd: {artCd}")
        
        images['artCd'] = artCd # 이미지 데이터에 artCd 추가
        
        return images

    except Exception as e:
        print(f"이미지 데이터 조회 오류: {e}")
        return {}

async def art_list_detail_views(request, artCd):
    """art_list에서 artCd에 해당하는 정보 가져오기"""
    try:
        art_list = request.session.get('art_list', [])
        art_info = next((art for art in art_list if art['artCd'] == artCd), {})

        return art_info

    except Exception as e:
        print(f"art_list 조회 오류: {e}")
        return {}

async def detail_view(request, artCd):
    try:
        # 이미지 데이터 가져오기
        images_data = await images(request, artCd)
        print(f"이미지 데이터: {images_data}")

        # art_list 정보 가져오기
        art_info_data = await art_list_detail_views(request, artCd)
        print(f"상세_art_info: {art_info_data}")

        # 필요한 정보 추출
        art_name = art_info_data.get('art_name', images_data.get('art_name', ''))
        file_url = images_data.get('file_url', art_info_data.get('file_url', ''))
        file_name = images_data.get('file_name', art_info_data.get('file_name', ''))
        art_width = images_data.get('art_width', art_info_data.get('art_width', ''))
        art_vrticl = images_data.get('art_vrticl', art_info_data.get('art_vrticl', ''))
        price = art_info_data.get('price', images_data.get('price', 0))

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
            'price': price,

        }


        print(f"잘 가져왔니? {context}")
        return render(request, 'detail.html', context)

    except Exception as e:
        print(f"상세 페이지 렌더링 오류: {e}")
        return render(request, 'detail.html', {'error_message': '상세 페이지를 불러오는 중 오류가 발생했습니다.'})
