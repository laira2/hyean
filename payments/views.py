from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import Order
import os


def create_order(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        new_order = Order(amount=amount)
        new_order.save()

        return JsonResponse({
            'order_id': new_order.order_id,
            'customer_key': new_order.customer_key,
            'amount': new_order.amount,
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def payment_success(request):
    return render(request, 'payments/payment_success.html')


def payment_fail(request):
    return render(request, 'payments/payment_fail.html')


def confirm_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_key = data.get('paymentKey')
        order_id = data.get('orderId')
        amount = data.get('amount')

        # 결제 확인 로직 구현
        # 예: Toss Payments API 호출하여 결제 확인

        # 성공 또는 실패 응답 반환
        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def payment_request(request):
    # 결제 요청을 위한 임시 주문 생성
    new_order = Order(amount=50000)
    new_order.save()

    context = {
        'order_id': new_order.order_id,
        'amount': new_order.amount,
        'customer_key': new_order.customer_key,
        'client_key': os.getenv('TOSS_PAYMENTS_CLIENT_KEY'),
    }
    return render(request, 'payments/payment_request.html', context)
