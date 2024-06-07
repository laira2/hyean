<<<<<<< HEAD
import random
import requests
import time
from django.shortcuts import render
from urllib.parse import urlencode

# OpenAPIView 클래스 정의
class OpenAPIView:
    pass

def openapi_view(request):
    base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
    image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"
    info_set = set()

    for page_number in range(1, 6):
        params = {
            "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
            "pageNo": str(page_number),
            "numOfRows": "10",
            "returnType": "json",
            "engNlty": "Republic of Korea"
        }

        full_url = base_url + '?' + urlencode(params)
        response = requests.get(full_url)

        if response.status_code == 200:
            data = response.json()
            items = data.get('response', {}).get('body', {}).get('items', [])
            if items:
                for item in items:
                    art_name = item.get('artNm')
                    if art_name:
                        art_name_stripped = art_name.strip()
                        if art_name_stripped:
                            info_set.add(art_name_stripped)

    info_list = list(info_set)

    image_info_dict = {}

    for art_name in info_list:
        image_params = {
            "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
            "pageNo": "1",
            "numOfRows": "10",
            "returnType": "json",
            "artNm": art_name
        }
        try:
            image_response = requests.get(image_api_url, params=image_params, timeout=20)
            if image_response.status_code == 200:
                image_data = image_response.json()
                image_items = image_data.get('response', {}).get('body', {}).get('items', [])
                if image_items:
                    for image_item in image_items:
                        file_name = image_item.get('fileNm', '')
                        file_url = image_item.get('fileUrl', '')
                        if file_name and file_url:
                            file_name_prefix = file_name[:4]
                            image_info_dict[file_name_prefix] = {
                                'art_name': art_name,
                                'file_name': file_name,
                                'file_url': file_url
                            }
            else:
                print(f"이미지를 가져오지 못했습니다. {art_name}. Status Code: {image_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"이미지를 가져오는 동안 오류가 발생했습니다. {art_name}: {e}")
            print("10초 후 다시 시도합니다.")
            time.sleep(10)

    for image_info in image_info_dict.values():
        price = random.randint(1000, 10000) * 10000
        image_info['price'] = price

    image_info_list = list(image_info_dict.values())
    return render(request, 'openapi.html', {'image_info_list': image_info_list})
=======
import random #난수 생성 함수 모듈
import asyncio #비동기 작업을 위한 asyncio 모듈
import aiohttp #비동기 HTTP 클라이언트 라이브러리인 aiohttp를 가져오며, 비동기적으로 HTTP 요청 및 응답을 받아올 수 있다.
import requests #동기적인 HTTP 요청을 보내는데 사용되는 requests 모듈을 가져온다. HTTP 요청/응답을 받아옴
import time #시간 관련 함수 제공
from django.shortcuts import render #장고에서 HTML 템프릿을 랜더링하기 위한 render함수 가져옴
from urllib.parse import urlencode #딕셔너리를 쿼리 문자열로 변환하는데 사용

# OpenAPIView 클래스 정의
class OpenAPIView: #templates의 openapi.html만 바라보게 하기 위해 사용
    pass

# 이미지 및 작품 데이터 캐싱을 위한 딕셔너리
cached_data = { #이미지와 작품 데이터를 캐싱하기 위해 딕셔너리 초기화
    'images': {}, #이미지 데이터 저장을 위해 사용되는 빈 딕셔너리
    'art_names': set() #작품명을 저장하는데 사용되는 빈 집합(set)
}

async def fetch(session, url): #비동기적으로 URL에서 데이터를 가져오는 함수로 'aiohttp'모듈 사용하여 비동기적으로 HTTP 요청
    async with session.get(url) as response:
        #async with는 비동기적으로 with문을 사용하기 위한 구문으로 자원관리를 위해 사용
        return await response.json()

async def get_image(session, url): #이미지 데이터를 가져오는데 사용되는 함수
    global cached_data #전역변수 선언, 해당 변수는 작품 데이터를 캐싱하기 위해 사용

    if url in cached_data['images']:
        return cached_data['images'][url]
    #이미지 데이터가 이미 캐싱되어있는지 확인, 캐싱되어있다면 캐싱된 데이터 반환

    async with session.get(url) as response:

        image_data = await response.json()
        cached_data['images'][url] = image_data
        #새로 가져온 이미지 데이터 저장
        return image_data

async def get_data(base_url):
    async with aiohttp.ClientSession() as session:
    #aiohttp의 Clientsession 객체를 사용, 비동기적으로 해당 URL에 GET요청
    #session은 HTTP 요청을 보내는데 사용
        tasks = [] #비동기 작업들을 저장할 빈 리스트 생성
        for page_number in range(0, 5):
            params = {
                "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
                "pageNo": str(page_number),
                "numOfRows": "100",
                "returnType": "json",
                "engNlty": "Republic of Korea"
            }
            full_url = base_url + '?' + urlencode(params)
            #기본 URL과 매개변수를 조합하여 전체 URL 생성
            tasks.append(fetch(session, full_url))
            #비동기 함수를 호출하여 생성된 URL에서 데이터를 가져오는 작업 생성 후 tasks리스트에 추가

        responses = await asyncio.gather(*tasks)
        #tasks리스트에 있는 모든 비동기 작업을 동시에 실행

        # 작품명 및 이미지 데이터 캐싱
        for response in responses: #비동기적으로 실행한 HTTP 요청 결과를 담고 있는 리스트로, 반복문 사용
            items = response.get('response', {}).get('body', {}).get('items', [])
            #각 응답에서 작품 정보를 추출하며, 위 내용중 하나라도 존재하지 않으면 빈 리스트 반환
            if items: #응답에서 추출한 작품 정보가 존재하는지 확인
                for item in items: #작품정보가 있을 경우 각 작품 정보에 대해 반복
                    art_name = item.get('artNm')
                    if art_name:
                        art_name_stripped = art_name.strip() #작품명 있을경우 양쪽 공배 제거 후 변수에 할당
                        if art_name_stripped:
                            cached_data['art_names'].add(art_name_stripped)
                            #캐싱된 데이터에 작품명 추가. 중복된 작품명은 자동 제거

        return responses

async def openapi_view(request):
    base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
    image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"

    data_responses = await get_data(base_url)
    #get_data 함수를 사용하여 작품 정보를 가져오며, 비동기적으로 실행된다.
    #await 키워드를 사용하여 결과를 기다림

    info_list = list(cached_data['art_names'])
    # 앞서 캐시된 작품명을 담고 있는 세트를 리스트로 변환하여 info_list 변수에 저장

    image_info_dict = {} #이미지 정보를 저장할 빈 딕셔너리 생성

    async with aiohttp.ClientSession() as session:
    #비동기 HTTP 요청을 수행하기 위해 aiohttp 모듈 사용하여 클라이언트 세션 생성
    #해당 세션은 HTTP 요청을 보내기 위한 컨텍스트 매니저로 사용
        for art_name in info_list: #이미지를 가져올 작품명을 info_list에서 작품명을 반복하여 가져옴
            image_params = { #이미지를 가져오기 위해 파라미터 설정
                "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
                "pageNo": "1",
                "numOfRows": "10",
                "returnType": "json",
                "artNm": art_name
            }
            try: #비동기적으로 이미지를 가져오는 작업 수행
                image_response = await get_image(session, image_api_url + '?' + urlencode(image_params))
                #get_image함수를 호출하여 이미지를 가져오며, await는 비동기 함수 결과를 기다리는데 사용, API URL, 매겨변수 포함 딕셔너리
                if image_response:
                    image_data = image_response.get('response', {}).get('body', {}).get('items', [])
                    #이미지가 있을 시 JSON 형식으로 데이터 추출
                    if image_data: #데이터 존재여부 확인
                        for image_item in image_data:
                            file_name = image_item.get('fileNm', '')
                            file_url = image_item.get('fileUrl', '')
                            if file_name and file_url: #파일이름과 URL이 빈값인지 확인, 값이 있다면 저장
                                file_name_prefix = file_name[:4] #파일명 접두사 4글자 추출
                                image_info_dict[file_name_prefix] = { #딕셔너리에 저장
                                    'art_name': art_name,
                                    'file_name': file_name,
                                    'file_url': file_url
                                }
                else:
                    print(f"이미지를 가져오지 못했습니다. {art_name}.")
            except aiohttp.ClientError as e:
                print(f"이미지를 가져오는 동안 오류가 발생했습니다. {art_name}: {e}") #작품명과 예외 객체 출력
                print("3초 후 다시 시도합니다.")
                await asyncio.sleep(3) #비동기 작업 일시 중단 후 3초 대기, 서버 부하 줄이기 위해 사용

    for image_info in image_info_dict.values(): #작품가격을 위한 랜덤함수 사용
        price = random.randint(1000, 10000) * 10000 #천에서 만사이의 랜덤 정수 선택 후 만 곱하기
        image_info['price'] = price

    image_info_list = list(image_info_dict.values()) #매개변수의 값을 리스트 형태로 반환하여 저장
    return render(request, 'openapi.html', {'image_info_list': image_info_list})
    #
>>>>>>> 15eb2b9a57a6374a0ab4842119a6c4990606e8ee
