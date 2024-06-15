from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    username = models.CharField(max_length=100)
    phone1 = models.CharField(max_length=4)
    phone2 = models.CharField(max_length=4)
    phone3 = models.CharField(max_length=4)
    email_name = models.EmailField()
    address = models.CharField(max_length=200)
    payment_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    artCd = models.CharField(max_length=20)
    art_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField()

    def __str__(self):
        return f"{self.art_name}"
