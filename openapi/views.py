import random
import aiohttp
import asyncio
from django.shortcuts import render
from urllib.parse import urlencode
from xml.etree import ElementTree  # XML 데이터를 파싱하기 위한 모듈 임포트
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

# 이미지 및 작품 데이터 캐싱을 위한 딕셔너리
cached_data = {
    'images': {},           # 이미지 데이터 캐시
    'art_names': set(),     # 작품명 캐시 (중복 방지를 위해 set으로 선언)
    'art_dimensions': {},   # 작품 가로, 세로 정보 캐시
    'art_info': {}          # 작품 정보 캐시
}

async def fetch(session, url, cache_key=None):
    """
    비동기 방식으로 URL에서 데이터를 가져오는 함수입니다.

    Args:
        session (aiohttp.ClientSession): aiohttp의 ClientSession 인스턴스
        url (str): 데이터를 가져올 URL
        cache_key (str): 데이터를 캐시할 때 사용할 키

    Returns:
        dict: 가져온 데이터의 JSON 형식
    """
    global cached_data

    # 캐시키가 존재하고 이미지 캐시에 있다면 캐시된 데이터 반환
    if cache_key and cache_key in cached_data['images']:
        return cached_data['images'][cache_key]

    async with session.get(url) as response:
        # XML 데이터를 가져와 파싱
        xml_data = await response.text()
        tree = ElementTree.fromstring(xml_data)
        json_data = {elem.tag: elem.text for elem in tree.iter()}

        # 캐시키가 존재한다면 캐시에 데이터 저장
        if cache_key:
            cached_data['images'][cache_key] = json_data

        return json_data

async def get_data(base_url):
    """
    공공데이터 API를 통해 데이터를 가져오는 함수입니다.

    Args:
        base_url (str): 기본 URL

    Returns:
        None
    """
    async with aiohttp.ClientSession() as session:
        tasks = []

        # 페이지 번호를 이용하여 여러 페이지에 걸쳐 데이터를 가져옴
        for page_number in range(0, 3):
            params = {
                "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8",
                "pageNo": str(page_number),
                "numOfRows": "10",
                "returnType": "xml",  # XML 형식으로 데이터 요청
                "engNlty": "Republic of Korea"
            }
            full_url = base_url + '?' + urlencode(params)
            tasks.append(fetch(session, full_url))

        # 비동기 방식으로 여러 개의 데이터를 가져와서 responses에 저장
        responses = await asyncio.gather(*tasks)

        # 가져온 데이터를 처리하여 캐시에 저장
        for response in responses:
            # 여기서 XML 데이터를 파싱하여 필요한 정보를 추출하고 캐싱하는 로직 추가
            # 예를 들어, ElementTree를 사용하여 필요한 정보를 추출할 수 있습니다.
            pass

@api_view(['GET'])
async def openapi_view(request):
    """
    Swagger API 명세서를 자동으로 작성하는 함수입니다.

    Args:
        request: 요청 객체

    Returns:
        render: 렌더링된 HTML 템플릿
    """
    # 이미지 및 작품 데이터 초기화
    cached_data = {
        'images': {},
        'art_names': set(),
        'art_dimensions': {},
        'art_info': {}
    }
  
    base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
    image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"

    # 데이터 가져오기
    await get_data(base_url)

    image_info_dict = {}

    async with aiohttp.ClientSession() as session:
        for artCd, info in cached_data['art_info'].items():
            art_name = info['artNm']
            art_width = cached_data['art_dimensions'][artCd].get('art_width', 0)
            art_vrticl = cached_data['art_dimensions'][artCd].get('art_vrticl', 0)
            categry = info['categry']

            # 이미지 데이터 가져오기
            image_params = {
                "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8",
                "pageNo": "1",
                "numOfRows": "5",
                "returnType": "json",
                "artCd": artCd
            }
            full_url = image_api_url + '?' + urlencode(image_params)
            image_response = await fetch(session, full_url, cache_key=full_url)
            if image_response:
                image_data = image_response.get('response', {}).get('body', {}).get('items', [])
                if image_data:
                    for image_item in image_data:
                        file_name = image_item.get('fileNm', '')
                        file_url = image_item.get('fileUrl', '')
                        if file_name and file_url:
                            file_name_prefix = file_name[:4]
                            # 작품 가격은 실제 값으로 대체
                            # 작가명 데이터가 없으면 빈 문자열로 설정
                            # 작가명 데이터 가져오기
                            artist_name = image_item.get('artistNm', '')

                            # 이미지 정보를 딕셔너리에 추가
                            image_info_dict[file_name_prefix] = {
                                'artCd': artCd,
                                'artNm': art_name,
                                'price': random.randint(1000, 10000) * 10000,
                                'artistNm': artist_name,
                                'categry': categry,
                                'artSize': f"{art_width}x{art_vrticl}"
                            }

                            # 이미지 정보 딕셔너리를 리스트로 변환
                            image_info_list = list(image_info_dict.values())

                            # HTML 템플릿에 이미지 정보 리스트 전달하여 렌더링
                            return render(request, 'openapi.html', {'image_info_list': image_info_list})
                          
