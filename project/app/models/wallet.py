import uuid

from django.db import models


class Wallet(models.Model):
    """
    Model to hold balance of a wallet and it's label. Balance can be changed only by creating connected transactions.
    Label field is indexed for quick search and ordering. Balance field is indexed for ordering
    """
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    balance = models.DecimalField(max_digits=50, decimal_places=18, default=0, db_index=True)

    def __str__(self):
        return f'{self.id}: {self.balance}'
