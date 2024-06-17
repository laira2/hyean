from django.db import models
import uuid

class Order(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer_key = models.UUIDField(editable=False, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order_id)

    def save(self, *args, **kwargs):
        if not self.customer_key:
            self.customer_key = uuid.uuid4()
        super(Order, self).save(*args, **kwargs)
