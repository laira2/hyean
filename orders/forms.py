# forms.py
from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['artCd', 'art_name', 'file_name', 'price', 'name', 'phone', 'email', 'address']
        widgets = {
            'artCd': forms.HiddenInput(),
            'art_name': forms.HiddenInput(),
            'file_name': forms.HiddenInput(),
            'price': forms.HiddenInput(),
        }
