import uuid

from django.db import models


class Transaction(models.Model):
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey('Wallet', related_name='transactions', on_delete=models.CASCADE)
    txid = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=50, decimal_places=18)

    def __str__(self):
        return f'{self.id}: {self.amount}'
