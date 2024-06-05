import random #판매가격 랜덤 생성을 위해 임포트
from django.shortcuts import render #Django의 render 함수를 사용
import requests #HTTP 요청을 보내기 위해 requests 모듈 사용
from urllib.parse import urlencode #URL을 생성할 때 필요한 쿼리 파라미터를 URL 인코딩하기 위해 사용
import time #timesleep 사용을 위해 임포트, 미사용 시 api 호출하면 timeout 발생

def openapi(request): #info_list 함수 정의
    # HTTP 요청을 처리하고 결과를 HTML 페이지에 랜더링하며, request 객체를 매개변수로 받는다.
    base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
    #기본 URL을 정의하며, 공공 데이터포털에서 제공하는 API의 엔트포인트를 가르킨다.
    image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"
    # 이미지를 불러오는 URL 정의
    info_set = set()  # 중복을 제거하기 위한 set 초기화

    for page_number in range(0, 30):  # 1부터 5까지의 페이지를 요청 (예시)
        params = { #API 요청에 필요한 파라미터 설정
            "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
            "pageNo": str(page_number),  # 페이지 번호 변경
            "numOfRows": "10", #가져올 데이터 1000개
            "returnType": "json", #파일 형식
            "engNlty": "Republic of Korea" #국가명 영문으로
        }

        full_url = base_url + '?' + urlencode(params)
        #파라미터를 URL에 추가하여 완전한 요청 URL을 생성

        response = requests.get(full_url) #생성한 요청 URL로 GET 요청 전달

        if response.status_code == 200: #요청이 성공했는지 확인하며, 200이면 데이터 수신 성공
            data = response.json() #응답 데이터를 JSON 형식으로 파싱하여 data 변수에 저장
            items = data.get('response', {}).get('body', {}).get('items', []) #JSON 데이터에서 작품 정보를 추출합니다. 이때 get 메서드를 사용하여 각 키에 대한 값을 안전하게 가져온다
            if items:  # 리스트가 비어있지 않은 경우에만 처리
                for item in items: #for문을 통해 작품명 추출
                    art_name = item.get('artNm')  # 작품명 가져오기
                    if art_name is not None:  #작품명이 None이 아닌 경우에만 처리
                        art_name_stripped = art_name.strip()  # 좌우 공백 제거
                        if art_name_stripped:  #공백이 아닌 경우에만 추가
                            info_set.add(art_name_stripped)  # 중복을 제거하기 위해 set에 추가

    info_list = list(info_set)  # 중복을 제거한 set을 다시 리스트로 변환
    print(info_list)  # 중복이 제거된 작품명 리스트 출력

    # 작품명을 이용하여 이미지 정보 가져오기
    image_info_dict = {}  # 파일명을 키로 가지는 딕셔너리 생성
    image_info_list = [] #빈 리스트 생성, 해당 리스트는 이미지 정보 저장 목적으로 사용된다.
    for art_name in info_list: #각각의 작품명에 대해 반복문을 실행
        image_params = { #각 작품명을 통해 이미지 정보를 가져오기 위한 파라미터 설정
            "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
            "pageNo": "0",  # 페이지 번호는 0으로 고정
            "numOfRows": "10",
            "returnType": "json",
            "artNm": art_name  # 작품명을 파라미터로 전달
        }
        try: #응답오류 예외 발생 시 처리하기 위해 설정
            image_response = requests.get(image_api_url, params=image_params, timeout=10)
            #request.get() 호출은 이미지 정보를 가져오기 위해 HTTP GET 요청을 보내며, URL, 파라미터, 10초 대기로 설정
            if image_response.status_code == 200: #요청이 성공적으로 처리되고 코드가 200이면 이미지 정보 추출
                image_data = image_response.json() #응답 데이터에서 이미지 정보 JSON 형식으로 받아와 파싱
                image_items = image_data.get('response', {}).get('body', {}).get('items', [])
                if image_items:
                    for image_item in image_items:
                        file_name = image_item.get('fileNm', '')
                        file_url = image_item.get('fileUrl', '')
                        if file_name and file_url:
                            file_name_prefix = file_name[:4] # 파일명의 앞 4글자를 추출하여 이미지 정보를 딕셔너리에 저장
                            image_info_dict[file_name_prefix] = {'art_name': art_name, 'file_name': file_name,
                                                                 'file_url': file_url}
                            # 파일명의 앞 4글자를 키로 가지는 딕셔너리의 값을 갱신하여 마지막 파일 정보 저장
                            last_file_info = {'art_name': art_name, 'file_name': file_name, 'file_url': file_url}
            else: #요청 실패했을 때 출력되는 구문
                print("이미지를 가져오지 못했습니다.", art_name, ". Status Code:", image_response.status_code)
        except requests.exceptions.RequestException as e: #요청 실패시 예외 발생, 아래 출력문으로 어떤 예외가 발생했는지 확인
            print("이미지를 가져오는 동안 오류가 발생했습니다.", art_name, ":", e)
            print("5초 후 다시 시도합니다.")
            time.sleep(5)  # 5초 동안 대기한 후 재시도

    # 가격을 랜덤으로 생성하여 작품 정보에 추가
    for image_info in image_info_dict.values():
        price = random.randint(1000, 10000) * 10000  # 랜덤 판매금액 만원 단위로 설정
        image_info['price'] = price

    # 중복을 제거한 이미지 정보 딕셔너리의 값들을 리스트로 변환하여 전달
    image_info_list = list(image_info_dict.values())

    # 작품명과 이미지 URL을 HTML 템플릿에 전달
    print(image_info_list) # 콘솔에 넘어온 데이터가 정상적으로 출력되는지 확인하기 위해 작성
    return render(request, 'openapi.html', {'image_info_list': image_info_list})