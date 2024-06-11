# artWork/views.py
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


def index(request):
    return render(request, 'index.html')

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def artwork_api(request):
    if request.method == 'GET':
        # 데이터 조회
        return Response({"message": "This is a GET request"}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        # 새로운 데이터 생성
        return Response({"message": "This is a POST request"}, status=status.HTTP_201_CREATED)
    elif request.method == 'PUT':
        # 기존 데이터 업데이트
        return Response({"message": "This is a PUT request"}, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        # 데이터 삭제
        return Response({"message": "This is a DELETE request"}, status=status.HTTP_204_NO_CONTENT)
      