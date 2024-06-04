from django.shortcuts import render
from .form import UserRegisterForm, LoginForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
# Create your views here.
def user_login(request):
    if request.method =='POST':
        login_form= LoginForm(request.POST)

        if login_form.is_valid(): #입력된 login_form 데이터 유효성 검사
            cd= login_form.cleaned_data # 통과된 유효성 데이터 (딕셔너리 형태)
            user=authenticate(request,username=cd['username'],password=cd['password']) #user 검증
        if user is not None:    # user 검증 통과 했을 경우
            if user.is_active:  #user가 active=True인 경우
                login(request,user) #login
                return HttpResponse('인증 성공') #추후 settings에서 LOGIN_REDIRECT_URL 지정 필요 ★★★★★★
            else:
                return HttpResponse('사용할 수 없는 계정')
        else:
            return HttpResponse('로그인 실패')
    else:
        login_form= LoginForm()
    return render(request,'login.html', {'login_form':login_form})


def register(request): #회원가입
    if request.method == "POST":
        register_form = UserRegisterForm(request.POST)
        if register_form.is_valid():
            new_user = register_form.save(commit=False)
            new_user.set_password(register_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'register_done.html',{"new_user":new_user})
    else: #POST 방식 외로 접근했을 때
        register_form=UserRegisterForm() 
    return render(request, 'register.html',{"register_form":register_form})