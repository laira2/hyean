from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username= forms.CharField(label="ID", widget=forms.TextInput(attrs={'class': 'id_input'}))
    password = forms.CharField(label="PW", widget=forms.PasswordInput(attrs={'class': 'id_input'}))

class UserRegisterForm(forms.ModelForm): #회원 가입 form
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput)  #비밀번호
    passwordcheck = forms.CharField(label="비밀번호 확인", widget=forms.PasswordInput) # 비밀 번호 확인
    address = forms.CharField(label="주소", widget=forms.TextInput)
    
    class Meta: #form 설정
        model = User  # User model연동
        fields = ['username', 'first_name','last_name', 'email', ] #User model에서 사용할 field 설정.
        # labels = {
        #     'username':'아이디',
        #     'first_name':'이름',
        #     'last_name':'성',
        #     'email':'이메일',
        # }
        # error_messages = {
        #     'username': {
        #         'required': '아이디를 입력해주세요.',
        #         'max_length': '아이디는 최대 150자까지 입력할 수 있습니다.',
        #         'invalid': '올바른 아이디를 입력해주세요. 허용되는 문자는 문자, 숫자, @/./+/-/_ 입니다.',
        #     },
        # }

    def clean_passwordcheck(self): #비밀번호 일치 여부 확인
        cd=self.cleaned_data
        if cd['password'] != cd['passwordcheck']:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return cd['passwordcheck']

    def clean_email(self): #이메일 존재 여부 확인
        cd=self.cleaned_data['email']
        if User.objects.filter(email=cd).exists():
            raise forms.ValidationError("이미 존재하는 이메일 입니다.")
        return cd


