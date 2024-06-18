import os
import base64
import json
import requests
from django.shortcuts import render
from dotenv import load_dotenv

load_dotenv()

def my_view(request):
    context = {
        'toss_payments_client_key': os.getenv('TOSS_PAYMENTS_CLIENT_KEY')
    }
    return render(request, 'checkout.html', context)

def checkout_view(request):
    orderId = request.POST.get('orderId')
    amount = request.POST.get('amount')
    return render(request, 'payments/checkout.html', {'orderId': orderId, 'amount': amount})

def success(request):
    orderId = request.GET.get('orderId')
    amount = request.GET.get('price')
    paymentKey = request.GET.get('paymentKey')

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

    return render(request, "payments/payment_success.html")

def fail(request):
    code = request.GET.get('code')
    message = request.GET.get('message')
    return render(request, "payments/payment_fail.html", {"code": code, "message": message})
