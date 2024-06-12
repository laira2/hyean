import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# 공공 API 엔드포인트 URL
BASE_URL = "http://apis.data.go.kr/5710000/benlService/"
ARTWORK_API_URL = f"{BASE_URL}nltyArtList"
IMAGE_API_URL = f"{BASE_URL}artImgList"

# 공공 API 키
API_KEY = "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8"

# API 요청에 필요한 파라미터
PAGE_NO = 1
NUM_OF_ROWS = 5

@api_view(['GET'])
def get_artwork_image(request):
    try:
        # 작품 정보 가져오기
        artwork_response = requests.get(ARTWORK_API_URL, params={
            "serviceKey": API_KEY,
            "pageNo": PAGE_NO,
            "numOfRows": NUM_OF_ROWS,
            # 다른 필요한 파라미터들 추가
        })
        artwork_response.raise_for_status()  # 오류가 발생하면 예외를 발생시킴
        artwork_data = artwork_response.json()  # JSON 응답을 딕셔너리로 파싱

        # 이미지 정보 가져오기
        image_response = requests.get(IMAGE_API_URL, params={
            "serviceKey": API_KEY,
            "pageNo": PAGE_NO,
            "numOfRows": NUM_OF_ROWS,
            # 다른 필요한 파라미터들 추가
        })
        image_response.raise_for_status()
        image_data = image_response.json()

        # 가져온 데이터를 적절히 가공하여 응답 데이터 구성
        response_data = {
            'artwork': artwork_data,
            'image': image_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        # 공공 API 요청 중 오류 발생 시
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        # 기타 오류 발생 시
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
