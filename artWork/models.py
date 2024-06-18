from django.db import models

class Product:
    name = models.CharField(max_length=100)
    description = models.TextField()

class Artwork(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    # 다른 필드들을 필요에 따라 추가

    def __str__(self):
        return self.name
