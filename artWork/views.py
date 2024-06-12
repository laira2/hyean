# views.py
from django.shortcuts import render
from urllib.parse import urlencode
from django.http import JsonResponse
import random
import asyncio
import aiohttp
import requests

cached_data = {
    'images': {},
    'art_names': set(),
    'art_dimensions': {},
    'art_info': {}
}


async def fetch(session, url, cache_key=None):
    global cached_data

    if cache_key and cache_key in cached_data['images']:
        return cached_data['images'][cache_key]

    async with session.get(url) as response:
        data = await response.json()

        if cache_key:
            cached_data['images'][cache_key] = data

        return data


async def get_data(base_url):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page_number in range(0, 3):
            params = {
                "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
                "pageNo": str(page_number),
                "numOfRows": "10",
                "returnType": "json",
                "engNlty": "Republic of Korea"
            }
            full_url = base_url + '?' + urlencode(params)
            tasks.append(fetch(session, full_url))

        responses = await asyncio.gather(*tasks)

        for response in responses:
            items = response.get('response', {}).get('body', {}).get('items', [])
            if items:
                for item in items:
                    art_name = item.get('artNm')
                    if art_name:
                        art_name_stripped = art_name.strip()
                        if art_name_stripped:
                            cached_data['art_names'].add(art_name_stripped)
                            art_width = item.get('artWidth')
                            art_vrticl = item.get('artVrticl')
                            artCd = item.get('artCd')
                            categry = item.get('categry') if item.get('categry') else '기타 '
                            cached_data['art_dimensions'][art_name_stripped] = {
                                'art_width': art_width,
                                'art_vrticl': art_vrticl
                            }
                            cached_data['art_info'][art_name_stripped] = {
                                'artCd': artCd,
                                'categry': categry
                            }


async def openapi_view(request):
    base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
    image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"

    await get_data(base_url)

    info_list = list(cached_data['art_names'])

    image_info_dict = {}
    async with aiohttp.ClientSession() as session:
        for art_name in info_list:
            image_params = {
                "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
                "pageNo": "1",
                "numOfRows": "5",
                "returnType": "json",
                "artNm": art_name
            }
            try:
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
                                image_info_dict[file_name_prefix] = {
                                    'art_name': art_name,
                                    'file_name': file_name,
                                    'file_url': file_url,
                                    'art_width': cached_data['art_dimensions'].get(art_name, {}).get('art_width', ''),
                                    'art_vrticl': cached_data['art_dimensions'].get(art_name, {}).get('art_vrticl', ''),
                                    'artCd': cached_data['art_info'].get(art_name, {}).get('artCd', ''),
                                    'categry': cached_data['art_info'].get(art_name, {}).get('categry', '')
                                }
                else:
                    print(f"이미지를 가져오지 못했습니다. {art_name}.")
            except aiohttp.ClientError as e:
                print(f"이미지를 가져오는 동안 오류가 발생했습니다. {art_name}: {e}")
                print("3초 후 다시 시도합니다.")
                await asyncio.sleep(3)

    for image_info in image_info_dict.values():
        price = random.randint(1000, 10000) * 10000

        image_info['price'] = price

    image_info_list = list(image_info_dict.values())
    return render(request, 'index.html', {'image_info_list': image_info_list})


def search(request):
    base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
    image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"

    search_query = request.GET.get('q', '')
    print(f"검색한내용 :{search_query}")

    params = {
        "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
        "pageNo": "1",
        "numOfRows": "5",
        "returnType": "json",
        "artNm": search_query
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'item' in data['response']['body']['items']:
            art_list = data['response']['body']['items']['item']
        else:
            art_list = []

        for art in art_list:
            image_params = {
                "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8",
            }
            image_response = requests.get(image_api_url, params=image_params)
            if image_response.status_code == 200:
                image_data = image_response.json()
                if 'item' in image_data['response']['body']['items']:
                    art["image_url"] = image_data['response']['body']['items']['item']['imgUrl']
                else:
                    art["image_url"] = None

        print("API 요청 실패:", response.status_code)
        art_list = []

    return render(request, 'index.html', {'art_list': art_list, 'search_query': search_query})


def index(request):
    return render(request, 'index.html')


def artwork_api(request):
    # 여기에 API 로직이 들어가야함
    data = {
        'message': 'This is the artwork API endpoint.'
    }
    return JsonResponse(data)



