import random
import requests
import time
from django.shortcuts import render
from urllib.parse import urlencode
#import sys
#sys.setrecursionlimit(10000)

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

