from django.db import models

# class Order(models.Model):
#     name = models.CharField(max_length=255)
#     customer_name = models.CharField(max_length=255)
#     amount = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.name
#
# class Payment(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.CharField(max_length=50)
#     payment_status = models.CharField(max_length=20, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"Payment {self.pk} - {self.payment_status}"
