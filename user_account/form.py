from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username= forms.CharField(label="ID", widget=forms.TextInput(attrs={'class': 'id_input'}))
    password = forms.CharField(label="PW", widget=forms.PasswordInput(attrs={'class': 'id_input'}))

class UserRegisterForm(forms.ModelForm): #회원 가입 form
    username = forms.CharField(label='', max_length=100, widget=forms.TextInput(
        attrs={'id': 'username', 'placeholder': '아이디를 입력하세요.', 'required': True}))
    password = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'id': 'password', 'placeholder': '비밀번호를 입력하세요', 'required': True}))
    password_check = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'id': 'password_check', 'placeholder': '비밀번호를 다시 입력해주세요', 'required': True}))
    email = forms.EmailField(label='', widget=forms.TextInput(
        attrs={'class': 'signup_email', 'placeholder': '이메일을 입력해주세요', 'required': True}))
    domain = forms.ChoiceField(
        choices=[('naver.com', 'naver.com'), ('daum.com', 'daum.com'), ('gmail.com', 'gmail.com'),
                 ('yahoo.com', 'yahoo.com')], widget=forms.Select(attrs={'id': 'domain'}))
    phone1 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'signup_phone', 'required': True}))
    phone2 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'signup_phone', 'required': True}))
    phone3 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'signup_phone', 'required': True}))
    address = forms.CharField(label='', widget=forms.TextInput(
        attrs={'id': 'address', 'placeholder': '주소를 입력해주세요', 'required': True}))
    detail_address = forms.CharField(label='', required=False, widget=forms.TextInput(
        attrs={'id': 'detail_address', 'placeholder': '상세주소를 입력해주세요'}))

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


