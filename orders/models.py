# models.py
from django.db import models
from django.utils import timezone

class Order(models.Model):
    artCd = models.CharField(max_length=50)
    art_name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    order_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.id} for {self.art_name}"

