import random  # 난수 생성 함수 모듈
import asyncio  # 비동기 작업을 위한 asyncio 모듈
import aiohttp  # 비동기 HTTP 클라이언트 라이브러리
from django.shortcuts import render  # 장고에서 HTML 템플릿을 렌더링하기 위한 render 함수
from urllib.parse import urlencode  # 딕셔너리를 쿼리 문자열로 변환하는데 사용
import hashlib
import time

class OpenAPIView:
    """templates의 openapi.html만 바라보게 하기 위해 사용"""
    pass

# 이미지 및 작품 데이터 캐싱을 위한 딕셔너리
cached_data = {  # 이미지와 작품 데이터를 캐싱하기 위해 딕셔너리 초기화
    'images': {},  # 이미지 데이터 저장을 위해 사용되는 빈 딕셔너리
    'art_names': set(),  # 작품명을 저장하는데 사용되는 빈 집합(set)
    'art_dimensions': {},  # 작품의 가로 세로 정보를 저장할 딕셔너리
    'art_info': {}  # 작품 id, 카테고리 정보를 저장할 딕셔너리
}

async def fetch(session, url, cache_key=None):
    """
    비동기적으로 데이터를 가져오고 캐싱처리 진행
    cache_key=None는 캐시 키로, 기본값이 None이며, 해당 키를 사용하여 데이터 캐시 진행
    """
    global cached_data  # 함수 내에서 cached_data를 수정하기 위해 전역변수 선언

    if cache_key and cache_key in cached_data['images']:  # cache_key가 주어졌고, 딕셔너리에 있다면
        return cached_data['images'][cache_key]  # 캐시된 데이터 반환

    async with session.get(url) as response:  # 비동기 실행 후, 응답을 response 변수에 저장 후 응답대기
        data = await response.json()  # 응답객체에서 json 데이터를 비동기적으로 추출 후 data 저장
        if cache_key:  # cache_key가 있는 경우 이미지값을 딕셔너리에 저장
            cached_data['images'][cache_key] = data
        return data  # 캐시키와 이미지값을 호출 시 반환

async def get_data(base_url, session):
    """비동기적으로 기본 데이터를 가져오고 캐싱"""
    tasks = []  # 비동기 작업들을 저장할 빈 리스트 생성
    for page_number in range(0, 5):
        params = {
            "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
            "pageNo": str(page_number),
            "numOfRows": "10",
            "returnType": "json",
            "engNlty": "Republic of Korea"
        }
        full_url = base_url + '?' + urlencode(params)  # 기본 URL과 매개변수를 조합하여 전체 URL 생성
        tasks.append(fetch(session, full_url))  # 비동기 함수를 호출하여 생성된 URL에서 데이터를 가져오는 작업 생성 후 tasks 리스트에 추가

    responses = await asyncio.gather(*tasks)  # tasks 리스트에 있는 모든 비동기 작업을 동시에 실행

    for response in responses:  # 비동기적으로 실행한 HTTP 요청 결과를 담고 있는 리스트로, 반복문 사용
        items = response.get('response', {}).get('body', {}).get('items', [])
        # 각 응답에서 작품 정보를 추출하며, 위 내용중 하나라도 존재하지 않으면 빈 리스트 반환
        if items:  # 응답에서 추출한 작품 정보가 존재하는지 확인
            for item in items:  # 작품 정보가 있을 경우 각 작품 정보에 대해 반복
                art_name = item.get('artNm')
                if art_name:
                    art_name_stripped = art_name.strip()  # 작품명 있을 경우 양쪽 공백 제거 후 변수에 할당
                    if art_name_stripped:
                        cached_data['art_names'].add(art_name_stripped) # 캐싱된 데이터에 작품명 추가. 중복된 작품은 추가하지 않는다.
                        artCd = hashlib.sha1(art_name_stripped.encode()).hexdigest()[:10] # 작품명을 해시하여 일련번호 생성
                        categry = item.get('categry') if item.get('categry') else '기타'  # 작품 카테고리, 없는 경우 기타 입력
                        cached_data['art_dimensions'][art_name_stripped] = {  # 가로, 세로 값 딕셔너리 저장
                            'art_width': generate_dimension(),
                            'art_vrticl': generate_dimension(),
                        }
                        cached_data['art_info'][art_name_stripped] = {  # 작품 일련번호, 카테고리 값 딕셔너리 저장
                            'artCd': artCd,
                            'categry': categry
                        }

async def get_image_data(image_api_url, session):
    """비동기적으로 이미지 데이터를 가져오고 캐싱"""
    image_info_dict = {}  # 이미지 정보를 저장할 빈 딕셔너리 생성
    tasks = []

    for art_name in cached_data['art_names']:  # 이미지를 가져올 작품명을 info_list에서 작품명을 반복하여 가져옴
        image_params = {  # 이미지를 가져오기 위해 파라미터 설정
            "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
            "pageNo": "1",
            "numOfRows": "10",
            "returnType": "json",
            "artNm": art_name
        }
        full_url = image_api_url + '?' + urlencode(image_params)  # 이미지 API의 전체 URL 생성
        print(f"작품명: {art_name}")
        tasks.append(fetch(session, full_url, cache_key=full_url))  # 이미지 데이터를 가져오는 비동기 함수 fetch 호출

    responses = await asyncio.gather(*tasks)  # tasks 리스트에 있는 모든 비동기 작업을 동시에 실행

    for image_response in responses:
        if image_response:
            image_data = image_response.get('response', {}).get('body', {}).get('items', [])
            # 이미지 데이터가 있는 경우 이미지 항목 추출 후 리스트 반환
            if image_data:
                for image_item in image_data:
                    art_name = image_item.get('artNm', '')  # 이미지 항목에서 작품명 가져오기
                    file_name = image_item.get('fileNm', '')
                    file_url = image_item.get('fileUrl', '')
                    if art_name and file_name and file_url:  # 작품명, 파일명, 파일 URL이 모두 존재하는 경우에만 처리
                        file_name_prefix = file_name[:4]  # 파일 이름 4글자 추출
                        #작품명과 작가명을 이용하여 일련번호 생성
                        artCd = generate_artCd(art_name, cached_data['art_info'].get(art_name, {}).get('artist_name', ''))
                        #가로와 세로 크기 랜덤하게 생성
                        art_width = generate_dimension()
                        art_vrticl = generate_dimension()
                        image_info_dict[file_name_prefix] = {  # 이미지 정보 딕셔너리에 저장
                            'art_name': art_name,
                            'file_name': file_name,
                            'file_url': file_url,
                            'art_width': art_width,
                            'art_vrticl': art_vrticl,
                            'artCd': artCd,
                            'categry': cached_data['art_info'].get(art_name, {}).get('categry', '')
                        }


    for image_info in image_info_dict.values():  # 작품 가격을 위한 랜덤함수 사용
        price = random.randint(1000, 10000) * 10000  # 천에서 만 사이의 랜덤 정수 선택 후 만 곱하기
        image_info['price'] = price

    return list(image_info_dict.values())  # 매개변수의 값을 리스트 형태로 반환하여 저장

def generate_artCd(art_name, artist_name):
    """작품명과 작가명을 이용하여 일련번호 생성"""
    unique_str = f"{art_name}_{artist_name}_{time.time()}_{random.randint(1000, 9999)}"  # 현재 시간과 랜덤 값으로 유니크한 문자열 생성
    return hashlib.sha1(unique_str.encode()).hexdigest()[:10]  # 유니크한 문자열을 해시하여 일련번호 생성

def generate_dimension(): #가로, 세로 크기 랜덤 생성
    return random.randint(50, 200)

async def openapi_view(request):
    """
    View 함수로, 비동기적으로 데이터를 가져오고 렌더링
    """
    base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
    image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"

    async with aiohttp.ClientSession() as session:  # aiohttp의 ClientSession 객체를 사용, 비동기적으로 해당 URL에 GET 요청
        await get_data(base_url, session)  # get_data 함수를 사용하여 작품 정보를 가져오며, 비동기적으로 실행
        image_info_list = await get_image_data(image_api_url, session)  # 이미지 정보를 비동기적으로 가져옴

    return render(request, 'openapi.html', {'image_info_list': image_info_list})  # 가져온 데이터를 템플릿에 전달하여 렌더링