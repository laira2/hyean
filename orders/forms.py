# forms.py
from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    artCd = forms.CharField(widget=forms.HiddenInput())
    art_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput())
    price = forms.DecimalField(max_digits=10, decimal_places=2,
                               widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    image_url = forms.URLField(widget=forms.HiddenInput())
    user = forms.CharField(widget=forms.HiddenInput())

    username = forms.CharField(label='', max_length=100, widget=forms.TextInput(
        attrs={'id': 'username', 'placeholder': '이름을 입력하세요.', 'required': True}))
    phone1 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'order_phone', 'required': True}))
    phone2 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'order_phone', 'required': True}))
    phone3 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'order_phone', 'required': True}))
    email_name = forms.CharField(label='', widget=forms.TextInput(
        attrs={'class': 'order_email', 'placeholder': '이메일을 입력해주세요', 'required': True}))
    address = forms.CharField(label='', widget=forms.TextInput(
        attrs={'id': 'address', 'placeholder': '주소를 입력해주세요', 'required': True}))