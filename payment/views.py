from django.contrib.sites import requests
from django.shortcuts import render

# Create your views here.
def pay (request):
    url = 'https://kapi.kakao.com/v1/payment/ready'
    data = {
        'cid': 'TC0ONETIME',
        'partner_order_id': '1111',
        'partner_user_id': '1111',
        'item_name': 'test',
        'quantity': 1,
        'total_amount': 1000,
        'vat_amount': 200,
        'tax_free_amount': 0,
        'approval_url': 'https://example.com/success',
        'cancel_url': 'https://example.com/cancel',
        'fail_url': 'https://example.com/fail'
    }
    headers = {
        'Authorization': 'KakaoAK {admin_key}'
    }
    response = requests.post(url, data=data, headers=headers)
    print(response.json())
    return render(request,'pay.html')