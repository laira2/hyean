from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random
import aiohttp
import asyncio
from urllib.parse import urlencode  # 수정된 부분

# openapi.views 모듈에서 필요한 함수 가져오기
from openapi.views import get_data, fetch  # 수정된 부분

# 전역 범위에서 cached_data 변수 정의
cached_data = {
    'images': {},           # 이미지 데이터 캐시
    'art_names': set(),     # 작품명 캐시 (중복 방지를 위해 set으로 선언)
    'art_dimensions': {},   # 작품 가로, 세로 정보 캐시
    'art_info': {}          # 작품 정보 캐시
}

def index(request):
    return render(request, 'index.html')

# 스키마 정의
artwork_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'artCd': openapi.Schema(type=openapi.TYPE_STRING, description='작품일련번호'),
        'artNm': openapi.Schema(type=openapi.TYPE_STRING, description='작품명'),
        'price': openapi.Schema(type=openapi.TYPE_INTEGER, description='작품 가격'),
        'artistNm': openapi.Schema(type=openapi.TYPE_STRING, description='작가명'),
        'categry': openapi.Schema(type=openapi.TYPE_STRING, description='카테고리'),
        'artSize': openapi.Schema(type=openapi.TYPE_STRING, description='작품 크기'),
        'fileUrl': openapi.Schema(type=openapi.TYPE_STRING, description='이미지 URL'),
    }
)

# 스키마 정의를 사용하여 Swagger API 명세서 추가
@swagger_auto_schema(
    method='get', 
    responses={200: openapi.Response("GET 요청 성공", artwork_schema)},
    tags=["Artwork API"]
)
@swagger_auto_schema(
    method='post', 
    responses={201: openapi.Response("POST 요청 성공")},
    tags=["Artwork API"]
)
@swagger_auto_schema(
    method='put', 
    responses={200: openapi.Response("PUT 요청 성공")},
    tags=["Artwork API"]
)
@swagger_auto_schema(
    method='delete', 
    responses={204: openapi.Response("DELETE 요청 성공")},
    tags=["Artwork API"]
)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def artwork_api(request):
    if request.method == 'GET':
        # 공공데이터 API에서 데이터를 가져오기
        base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
        image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"

        # asyncio 이벤트 루프 생성 및 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_data(base_url))

        info_list = list(cached_data['art_names'])
        image_info_dict = {}

        async def fetch_images():
            async with aiohttp.ClientSession() as session:
                for art_name in info_list:
                    image_params = {
                        "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
                        "pageNo": "1",
                        "numOfRows": "5",
                        "returnType": "json",
                        "artNm": art_name
                    }
                    full_url = image_api_url + '?' + urlencode(image_params)  # 수정된 부분
                    image_response = await fetch(session, full_url, cache_key=full_url)
                    if image_response:
                        image_data = image_response.get('response', {}).get('body', {}).get('items', [])  # 수정된 부분
                        if image_data:
                            for image_item in image_data:
                                file_name = image_item.get('fileNm', '')
                                file_url = image_item.get('fileUrl', '')
                                if file_name and file_url:
                                    file_name_prefix = file_name[:4]
                                    image_info_dict[file_name_prefix] = {
                                        'artCd': cached_data['art_info'].get(art_name, {}).get('artCd', ''),
                                        'artNm': art_name,
                                        'price': random.randint(1000, 10000) * 10000,
                                        'artistNm': cached_data['art_info'].get(art_name, {}).get('artistNm', '작가명 미상'),
                                        'categry': cached_data['art_info'].get(art_name, {}).get('categry', '기타'),
                                        'artSize': f"{cached_data['art_dimensions'].get(art_name, {}).get('art_width', '0')}x{cached_data['art_dimensions'].get(art_name, {}).get('art_vrticl', '0')}",
                                        'fileUrl': file_url,
                                    }

        loop.run_until_complete(fetch_images())

        image_info_list = list(image_info_dict.values())
        return Response(image_info_list, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        return Response({"message": "This is a POST request"}, status=status.HTTP_201_CREATED)
    elif request.method == 'PUT':
        return Response({"message": "This is a PUT request"}, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        return Response({"message": "This is a DELETE request"}, status=status.HTTP_204_NO_CONTENT)


# openapi 폴더의 views.py 파일은 공공데이터 API를 통해 데이터를 가져와서 처리하고, 
# artWork 폴더의 views.py 파일은 Swagger API 명세서를 작성하고 응답을 생성하는 역할을 합니다.