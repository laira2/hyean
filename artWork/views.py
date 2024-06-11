# artWork/views.py
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def index(request):
    return render(request, 'index.html')
  
@swagger_auto_schema(
    method='get', 
    responses={200: openapi.Response("This is a GET request")}
)
@swagger_auto_schema(
    method='post', 
    responses={201: openapi.Response("This is a POST request")}
)
@swagger_auto_schema(
    method='put', 
    responses={200: openapi.Response("This is a PUT request")}
)
@swagger_auto_schema(
    method='delete', 
    responses={204: openapi.Response("This is a DELETE request")}
)

#return Response({"message": 내용 입력해야함
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def artwork_api(request):
    if request.method == 'GET':
        # 데이터 조회
        return Response({"Artwork name": "Mang Hae dda",
                        "Artist name":"라이터",
                         "message": "불지르고 싶다",
                         "price": "23,000,000원",
                         "a.k.a": "방화범",
                         
                         }, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        # 새로운 데이터 생성
        return Response({"message": "This is a POST request"}, status=status.HTTP_201_CREATED)
    elif request.method == 'PUT':
        # 기존 데이터 업데이트
        return Response({"message": "This is a PUT request"}, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        # 데이터 삭제
        return Response({"message": "This is a DELETE request"}, status=status.HTTP_204_NO_CONTENT)