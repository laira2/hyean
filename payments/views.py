import os

from django.shortcuts import render
import requests, json, base64
from dotenv import load_dotenv
from orders.models import Ordered
from django.views.decorators.csrf import csrf_exempt

load_dotenv()

def my_view(request):
    context = {
        'toss_payments_client_key': os.getenv('TOSS_PAYMENTS_CLIENT_KEY')
    }
    return render(request, 'checkout.html', context)


def checkout_view(request):

    return render(
        request,
        'payments/checkout.html',
        )

# 결제가 완료되고 orders/ordered에 저장할 메서드
@csrf_exempt
def confirm_payment(request):
    if request.method == 'POST':
        data = request.json()  # JSON 데이터 가져오기
        # JSON 데이터에서 필요한 정보 추출
        paymentKey = data.get('paymentKey')
        orderId = data.get('orderId')
        amount = data.get('amount')

        try:
            # Ordered 모델에 저장 예시
            ordered = Ordered.objects.create(payment_key=paymentKey, order_id=orderId, amount=amount)
            ordered.save()

            return JsonResponse({'message': 'Payment confirmed and saved.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST method required.'}, status=405)