# artWork/views.py
from django.shortcuts import render
import random #난수 생성 함수 모듈
import asyncio #비동기 작업을 위한 asyncio 모듈
import aiohttp #비동기 HTTP 클라이언트 라이브러리인 aiohttp를 가져오며, 비동기적으로 HTTP 요청 및 응답을 받아올 수 있다.
from django.shortcuts import render #장고에서 HTML 템프릿을 랜더링하기 위한 render함수 가져옴
from urllib.parse import urlencode #딕셔너리를 쿼리 문자열로 변환하는데 사용

# def index(request):
#     return render(request, 'index.html')

# 이미지 및 작품 데이터 캐싱을 위한 딕셔너리
cached_data = { #이미지와 작품 데이터를 캐싱하기 위해 딕셔너리 초기화
    'images': {}, #이미지 데이터 저장을 위해 사용되는 빈 딕셔너리
    'art_names': set(), #작품명을 저장하는데 사용되는 빈 집합(set)
    'art_dimensions': {}, #작품의 가로 세로 정보를 저장할 딕셔너리 추가
    'art_info': {} #작품 id, 카테고리 정보를 저장할 딕셔너리 추가
}

async def fetch(session, url, cache_key=None):
#비동기적으로 데이터를 가져오고 캐싱처리 진행
#cache_key=None는 캐시 키로, 기본값이 None이며, 해당 키를 사용하여 데이터 캐시 진행
    global cached_data # 함수 내에서 cached_data를 수정하기 위해 전역변수 선언

    if cache_key and cache_key in cached_data['images']: #cache_key가 주어졌고, 딕셔너리에 있다면
        return cached_data['images'][cache_key] #캐시된 데이터 반환

    async with session.get(url) as response: #비동기 실행 후, 응답을 response 변수에 저장 후 응답대기
        data = await response.json() #응답객체에서 json 데이터를 비동기적으로 추출 후 data 저장

        if cache_key: #cache_key가 있는 경우 이미지값을 딕셔너리에 저장
            cached_data['images'][cache_key] = data

        return data #캐시키와 이미지값을 호출 시 반환

async def get_data(base_url):
    async with aiohttp.ClientSession() as session:
    #aiohttp의 Clientsession 객체를 사용, 비동기적으로 해당 URL에 GET요청
    #session은 HTTP 요청을 보내는데 사용
        tasks = [] #비동기 작업들을 저장할 빈 리스트 생성
        for page_number in range(0, 3):
            params = {
                "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
                "pageNo": str(page_number),
                "numOfRows": "10",
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
                            art_width = item.get('artWidth') #작품 가로
                            art_vrticl = item.get('artVrticl') #작품 세로
                            artCd = item.get('artCd') #작품 id
                            categry = item.get('categry') if item.get('categry') else '기타 '#작품 카테고리, 없는 경우 기타 입력
                            cached_data['art_dimensions'][art_name_stripped] = { #가로, 세로 값 딕셔너리 저장
                                'art_width': art_width,
                                'art_vrticl': art_vrticl
                            }
                            cached_data['art_info'][art_name_stripped] = { #작품 일련번호, 카테고리 값 딕셔너리 저장
                                'artCd': artCd,
                                'categry': categry
                            }

async def openapi_view(request):
    base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
    image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"

    await get_data(base_url)
    #get_data 함수를 사용하여 작품 정보를 가져오며, 비동기적으로 실행된다.
    #await 키워드를 사용하여 결과를 기다림

    info_list = list(cached_data['art_names'])
    #앞서 캐시된 작품명을 담고 있는 세트를 리스트로 변환하여 info_list 변수에 저장

    image_info_dict = {}
    #이미지 정보를 저장할 빈 딕셔너리 생성

    async with aiohttp.ClientSession() as session:
    #비동기 HTTP 요청을 수행하기 위해 aiohttp 모듈 사용하여 클라이언트 세션 생성
    #해당 세션은 HTTP 요청을 보내기 위한 컨텍스트 매니저로 사용
        for art_name in info_list: #이미지를 가져올 작품명을 info_list에서 작품명을 반복하여 가져옴
            image_params = { #이미지를 가져오기 위해 파라미터 설정
                "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
                "pageNo": "1",
                "numOfRows": "5",
                "returnType": "json",
                "artNm": art_name
            }
            try: #비동기적으로 이미지를 가져오는 작업 수행
                full_url = image_api_url + '?' + urlencode(image_params)
                #이미지 API의 전체 URL 생성
                image_response = await fetch(session, full_url, cache_key=full_url)
                #이미지 데이터를 가져오는 비동기 함수 fetch 호출
                #전체 URL로 HTTP GET요청 후 이미지 데이터 반환
                #캐시되어 이전에 가져온 데이터가 있는 경우 캐시된 데이터 반환
                if image_response:
                    image_data = image_response.get('response', {}).get('body', {}).get('items', [])
                    #이미지 데이터가 있는 경우 이미지 항목 추출 후 리스트 반환
                    if image_data:
                        for image_item in image_data:
                            file_name = image_item.get('fileNm', '')
                            file_url = image_item.get('fileUrl', '')
                            if file_name and file_url:
                                file_name_prefix = file_name[:4] #파일 이름 4글자 추출
                                image_info_dict[file_name_prefix] = { #이미지 정보 딕셔너리에 저장
                                    'art_name': art_name,
                                    'file_name': file_name,
                                    'file_url': file_url,
                                    'art_width': cached_data['art_dimensions'].get(art_name, {}).get('art_width', ''),
                                    'art_vrticl': cached_data['art_dimensions'].get(art_name, {}).get('art_vrticl', ''),
                                    'artCd': cached_data['art_info'].get(art_name, {}).get('artCd', ''),
                                    'categry': cached_data['art_info'].get(art_name, {}).get('categry', '')
                                }
                else:
                    print(f"이미지를 가져오지 못했습니다. {art_name}.") #이미지 데이터가 없는경우 작품명 출력
            except aiohttp.ClientError as e:
                print(f"이미지를 가져오는 동안 오류가 발생했습니다. {art_name}: {e}") #오류발생 시 세부정보와 작품명 출력
                print("3초 후 다시 시도합니다.") #네트워크 등의 오류 발생 시 3초 대기 문구 출력
                await asyncio.sleep(3) #3초 대기, 비동기적으로 일시 중단 후 지정 시간 후 코드 실행

    for image_info in image_info_dict.values(): #작품가격을 위한 랜덤함수 사용
        price = random.randint(1000, 10000) * 10000 #천에서 만사이의 랜덤 정수 선택 후 만 곱하기
        image_info['price'] = price

    image_info_list = list(image_info_dict.values()) #매개변수의 값을 리스트 형태로 반환하여 저장
    return render(request, 'index.html', {'image_info_list': image_info_list})

# async def search_view(request): # 작품명으로 검색 기능 메서드
#     base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
#     await get_data(base_url)
#
#     if request.method == 'GET':
#         # search_form =
#
#     search_query = request.GET.get('search_query', '').strip()
#     filtered_art_names = [art_name for art_name in cached_data['art_names'] if search_query in art_name]
#
#     return render(request, 'index.html', {'filtered_art_names': filtered_art_names})
