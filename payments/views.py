import os
from django.http import HttpResponse
import base64
import json
import requests
from django.shortcuts import render
from dotenv import load_dotenv
from orders.models import Ordered
from orders.models import Order, OrderItem
from django.views.decorators.csrf import csrf_exempt

load_dotenv()

def my_view(request, order_id):
    order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    item = order.orderitem_set.first()
    print(f"my_view의 item : {item}")
    context = {
            'order_id': order_id,
            'email': order.email,
            'name': order.name,
            'phone': order.phone,
            'total_price': order.total_price,
            'artCd': item.artCd,
            'toss_payments_client_key': 'test_gck_docs_Ovk5rk1EwkEbP0W43n07xlzm'
        }
    print(f"my_view의 context : {context}")
    return render(request, 'payments/checkout.html', context)
def checkout_view(request):
  
    return render(request, 'payments/checkout.html',)


# 결제가 완료되고 orders/ordered에 저장할 메서드
@csrf_exempt
def confirm_payment(request):
    if request.method == 'POST':
        try:
            # 요청 본문을 바이트 문자열로 가져오기
            request_body = request.body

            # 바이트 문자열을 Python 데이터 구조로 변환
            data = json.loads(request_body)

            # JSON 데이터에서 필요한 정보 추출
            payment_id = data.get('paymentKey')
            payment_status = True  # 결제 성공
            paid_amount = data.get('amount')
            order_number = data.get('orderId')
            print(f"confirm : {data}")
            print(paid_amount)

            # Order 객체 가져오기
            order = Order.objects.filter(user=request.user).order_by('-created_at').first()
            print(f"confirm : {data}")

            # Ordered 모델에 저장
            ordered = Ordered.objects.create(
                order=order,
                payment_id=payment_id,
                payment_status=payment_status,
                paid_amount=paid_amount,
                order_number=order_number
            )
            ordered.save()

            # 템플릿을 렌더링하여 HTTP 응답 반환
            return render(request, 'account.html', {'message': 'Payment confirmed and saved.'})
        except (ValueError, KeyError, Exception) as e:
            # 에러 페이지를 렌더링하여 HTTP 응답 반환
            return HttpResponse(f'<h1>Error</h1><p>{str(e)}</p>', content_type='text/html', status=500)
    else:
        # 405 Method Not Allowed 응답 반환
        return HttpResponse('<h1>Method Not Allowed</h1><p>POST method required.</p>', content_type='text/html', status=405)

def success(request):
    orderId = request.GET.get('orderId')
    amount = request.GET.get('price')
    paymentKey = request.GET.get('paymentKey')
    order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    order_items = OrderItem.objects.filter(order=order)


    url = "https://api.tosspayments.com/v1/payments/confirm"
    secretKey = os.getenv('TOSS_PAYMENTS_SECRET_KEY')
    encoded_u = base64.b64encode(f"{secretKey}:".encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_u}",
        "Content-Type": "application/json"
    }

    params = {
        "orderId": orderId,
        "amount": amount,
        "paymentKey": paymentKey,
    }

    res = requests.post(url, json=params, headers=headers)
    res.json()  # If you need to use this response, handle it appropriately

    return render(request, "payments/payment_success.html", {
        'order_datetime': order.created_at,
        'name': order.name,
        'phone': order.phone,
        'address': order.address,
        'order_items': order_items,
        'orderId': orderId,
        'email': order.email,
    })

def fail(request):
    code = request.GET.get('code')
    message = request.GET.get('message')
    return render(request, "payments/payment_fail.html", {"code": code, "message": message})
