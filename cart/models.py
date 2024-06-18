from django.contrib.auth.models import User
from django.db import models

class Cart(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s cart"
class CartAddedItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    artCd = models.CharField(max_length=30)
    art_name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.art_name}"
