from django.shortcuts import render
from django.conf import settings

def payment_request(request, order_id):
    context = {
        'portone_store_id': settings.PORTONE_STORE_ID,
        'portone_api_key': settings.PORTONE_API_KEY,
        'portone_api_secret': settings.PORTONE_API_SECRET,
        'order_id': order_id,
    }
    return render(request, 'payments/payment_request.html', context)

def payment_success(request):
    return render(request, 'payments/payment_success.html')

def payment_fail(request):
    return render(request, 'payments/payment_fail.html')

def payment_checkout(request):
    return render(request, 'payments/checkout.html')

