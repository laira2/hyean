# forms.py
from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    artCd = forms.CharField(widget=forms.HiddenInput())  # 숨겨진 필드들
    art_name = forms.CharField(widget=forms.HiddenInput())
    file_name = forms.CharField(widget=forms.HiddenInput())
    price = forms.DecimalField(widget=forms.HiddenInput())

    username = forms.CharField(label='', max_length=100, widget=forms.TextInput(
        attrs={'id': 'username', 'placeholder': '이름을 입력하세요.', 'required': True}))
    phone1 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'signup_phone', 'required': True}))
    phone2 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'signup_phone', 'required': True}))
    phone3 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'signup_phone', 'required': True}))
    email_name = forms.CharField(label='', widget=forms.TextInput(
        attrs={'class': 'signup_email', 'placeholder': '이메일을 입력해주세요', 'required': True}))
    address = forms.CharField(label='', widget=forms.TextInput(
        attrs={'id': 'address', 'placeholder': '주소를 입력해주세요', 'required': True}))

    class Meta:
        model = Order
        fields = ['artCd', 'art_name', 'file_name', 'price', 'username', 'phone', 'email', 'address']
