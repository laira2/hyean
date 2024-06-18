# orders/forms.py

from django import forms
from .models import Order

class OrderForm(forms.ModelForm):

    artCd = forms.CharField(widget=forms.HiddenInput)
    art_name = forms.CharField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(widget=forms.HiddenInput, initial=1)
    price = forms.DecimalField(widget=forms.HiddenInput)
    image_url = forms.URLField(widget=forms.HiddenInput)

    name = forms.CharField(label='이름', max_length=100, widget=forms.TextInput(attrs={'placeholder': '이름','class':'form-control'}))
    phone = forms.CharField(label='전화번호', max_length=20, widget=forms.TextInput(attrs={'placeholder': '010-0000-0000','class':'form-control'}))
    email = forms.EmailField(label='이메일', max_length=100, widget=forms.EmailInput(attrs={'placeholder': 'name@example.com','class':'form-control'}))
    address = forms.CharField(label='배송지 주소', max_length=255, widget=forms.TextInput(attrs={'placeholder': '상세한 주소 작성해주세요.','class':'form-control'}))

    class Meta:
        model = Order
        fields = ['name', 'phone', 'email', 'address']
