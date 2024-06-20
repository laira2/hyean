from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .form import UserRegisterForm, LoginForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from orders.models import Order, OrderItem,Ordered

from .models import Profile
import uuid

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('account')  # 수정 후 리디렉션할 URL
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'user_info_update.html', context)

def user_login(request):
    if request.method =='POST':
        login_form= LoginForm(request.POST)
        if login_form.is_valid(): #입력된 login_form 데이터 유효성 검사
            cd= login_form.cleaned_data # 통과된 유효성 데이터 (딕셔너리 형태)
            user=authenticate(request,username=cd['username'],password=cd['password']) #user 검증
        if user is not None:    # user 검증 통과 했을 경우
            if user.is_active:  #user가 active=True인 경우
                login(request,user) #login
                return redirect('index')
            else:
                message="사용할 수 없는 계정입니다."
        else:
            message = "아이디 또는 비밀번호를 다시 확인해주세요."
    else:
        login_form= LoginForm()
        message=None

    return render(request,'login.html', {'login_form':login_form,'message':message})


def signup(request): #회원가입
    if request.method == "POST":
        signup_form = UserRegisterForm(request.POST)  # --register_form 을 signup_form으로 이름 바꿔주기--완료
        if signup_form.is_valid():
            new_user = signup_form.save(commit=False)
            new_user.set_password(signup_form.cleaned_data['password']) #set_password로 저장 전 해시 처리
            new_user.uuid = uuid.uuid4()  # uuid4()를 사용해서 랜덤 uuid 생성
            new_user.save()
            phone_number = signup_form.cleaned_data['phone1'] + signup_form.cleaned_data['phone2'] + signup_form.cleaned_data['phone3']
            address = signup_form.cleaned_data['address']
            detail_address = signup_form.cleaned_data['detail_address']
            profile = Profile.objects.create(user=new_user, phone_number=phone_number, address=address,
                                             detail_address=detail_address)
            return redirect('login')
    else: #POST 방식 외로 접근했을 때
        signup_form=UserRegisterForm()
    return render(request, 'signup.html',{"signup_form":signup_form})
@login_required
def account(request):
    user = request.user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    ordered_list=[]
    if orders:
        for order in orders:
            ordered_value  = Ordered.objects.filter(order=order)
            ordered_list.extend(ordered_value)

        return render(request, 'account.html',{'user':user, 'ordered_list':ordered_list})
    else:
        message = "주문 내역이 없습니다."
        return render(request, 'account.html', {'message': message})

def ordered_detail(request, order_number):
    print("order_number:",order_number)
    ordered = Ordered.objects.get(order_number=order_number)
    print("ordered:", ordered)
    order = ordered.order.orderitem_set.all()
    print("order:", order)

    return render (request, 'ordered_detail.html',{'ordered':ordered,'order':order})

@login_required
def delete_account(request):
    if request.user.is_authenticated:
        request.user.delete()
        logout(request)
        request.session.flush()
        return redirect('index')
    return redirect('login.html')