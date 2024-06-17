from django.db import models
from django.contrib.auth.models import User
class Order(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artCd = models.CharField(max_length=100)
    art_name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField()

    def __str__(self):
        return f"주문 #{self.id} - {self.art_name}"
