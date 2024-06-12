import random
import aiohttp
import asyncio
from django.shortcuts import render
from urllib.parse import urlencode
from xml.etree import ElementTree
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import hashlib
import time

class OpenAPIView:
    """templates의 openapi.html만 바라보게 하기 위해 사용"""
    pass

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

    try:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            data = await response.json()
            if cache_key:
                cached_data['images'][cache_key] = data
            return data
    except aiohttp.ClientError as e:
        print(f"HTTP 요청 오류: {e}")
        return None

async def get_data(base_url, session):
    """비동기적으로 기본 데이터를 가져오고 캐싱"""
    tasks = []
    for page_number in range(0, 5):
        params = {
            "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8",
            "pageNo": str(page_number),
            "numOfRows": "10",
            "returnType": "json",
            "engNlty": "Republic of Korea"
        }
        full_url = base_url + '?' + urlencode(params)
        tasks.append(fetch(session, full_url))

    responses = await asyncio.gather(*tasks)

    for response in responses:
        if response is None:
            continue
        items = response.get('response', {}).get('body', {}).get('items', [])
        if items:
            for item in items:
                art_name = item.get('artNm')
                if art_name:
                    art_name_stripped = art_name.strip()
                    if art_name_stripped:
                        cached_data['art_names'].add(art_name_stripped)
                        artCd = hashlib.sha1(art_name_stripped.encode()).hexdigest()[:10]
                        categry = item.get('categry') if item.get('categry') else '기타'
                        cached_data['art_dimensions'][art_name_stripped] = {
                            'art_width': generate_dimension(),
                            'art_vrticl': generate_dimension(),
                        }
                        cached_data['art_info'][art_name_stripped] = {
                            'artCd': artCd,
                            'categry': categry
                        }

async def get_image_data(image_api_url, session):
    """비동기적으로 이미지 데이터를 가져오고 캐싱"""
    image_info_dict = {}
    tasks = []

    for art_name in cached_data['art_names']:
        params = {
            "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
            "title": art_name,
            "numOfRows": "1",
            "returnType": "json",
            "pageNo": "1"
        }
        full_url = image_api_url + '?' + urlencode(params)
        tasks.append(fetch(session, full_url, art_name))

    responses = await asyncio.gather(*tasks)
    for response in responses:
        if response:
            title = response.get('title')
            if title:
                image_info_dict[title] = response

    cached_data['images'] = image_info_dict

def generate_dimension():
    """임의의 작품 크기(가로 또는 세로)를 생성합니다."""
    return random.randint(50, 200)
