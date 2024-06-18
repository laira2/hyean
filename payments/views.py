import os

from django.shortcuts import render
import requests, json, base64
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

    return render(
        request,
        'payments/checkout.html',
        {'orderId': orderId, 'amount': amount})

def success(request):
    orderId = request.GET.get('orderId')
    amount = request.GET.get('price')
    paymentKey = request.GET.get('paymentKey')

    url = "https://api.tosspayments.com/v1/payments/confirm"

    """
      개발자센터에 로그인해서 내 결제위젯 연동 키 > 시크릿 키를 입력하세요. 시크릿 키는 외부에 공개되면 안돼요.
      @docs https://docs.tosspayments.com/reference/using-api/api-keys
    """
    secretKey = os.getenv('TOSS_PAYMENTS_SECRET_KEY')
    userpass = f"{secretKey}:"
    encoded_u = base64.b64encode(userpass.encode()).decode()


    """
      토스페이먼츠 API는 시크릿 키를 사용자 ID로 사용하고, 비밀번호는 사용하지 않습니다.
      비밀번호가 없다는 것을 알리기 위해 시크릿 키 뒤에 콜론을 추가합니다.
      @docs https://docs.tosspayments.com/reference/using-api/authorization#basic-인증-방식이란
    """

    headers = {
        "Authorization": "Basic %s" % encoded_u,
        "Content-Type": "application/json"
    }

    params = {
        "orderId": orderId,
        "amount": amount,
        "paymentKey": paymentKey,
    }

    """
      결제 승인 API를 호출하세요.
      결제를 승인하면 결제수단에서 금액이 차감돼요.
      @docs https://docs.tosspayments.com/guides/payment-widget/integration#3-결제-승인하기
    """
    res = requests.post(url, data=json.dumps(params), headers=headers)
    resjson = res.json()
    pretty = json.dumps(resjson, indent=4)

    # if res.status_code == 200:
    #     respaymentKey = resjson["paymentKey"]
    #     resorderId = resjson["orderId"]
    #     restotalAmount = resjson["totalAmount"]
    #
    #     return render(
    #         request,
    #         "payments/payment_success.html",
    #         {
    #             "res": pretty,
    #             "respaymentKey": respaymentKey,
    #             "resorderId": resorderId,
    #             "restotalAmount": restotalAmount,
    #         }
    #     )
    # else:
    #     rescode = resjson["code"]
    #     resmessage = resjson["message"]
    #     return render(
    #         request,
    #         "payments/payment_fail.html",
    #         {
    #             "code": rescode,
    #             "message": resmessage
    #         }
    #     )
    return render(request, "payments/payment_success.html")

def fail(request):
    code = request.GET.get('code')
    message = request.GET.get('message')

    return render(
        request,
        "payments/payment_fail.html",
        {
            "code": code,
            "message": message,
        }
    )