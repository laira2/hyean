# payments/models.py
from django.db import models

class Order(models.Model):
    name = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
