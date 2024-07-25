import uuid

from django.db import models


class Wallet(models.Model):
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255, null=True, blank=True)
    balance = models.DecimalField(max_digits=50, decimal_places=18, default=0)

    def __str__(self):
        return f'{self.id}: {self.balance}'
