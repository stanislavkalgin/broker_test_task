import uuid
from decimal import Decimal

from django.db import models, transaction

from .wallet import Wallet
from ..exceptions import NegativeBalanceException


class Transaction(models.Model):
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    wallet = models.ForeignKey('Wallet', related_name='transactions', on_delete=models.RESTRICT)
    txid = models.CharField(max_length=255, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=50, decimal_places=18)

    def save(self, *args, **kwargs):
        """
        Custom save method to ensure wallet balance integrity.
        This method implements the ledger system approach, where the current balance
        is stored in the Wallet model and updated with each transaction. It ensures
        atomicity and consistency using database transactions and row locking.

        The approach used here is a good fit for applications requiring:
        - Real-time balance updates.
        - High transactional throughput.
        - Simple and direct balance access.

        Alternative Approaches:
        1. **Event Sourcing**: Instead of directly updating the balance, we can store each
           transaction as an event and derive the balance by replaying events. This approach
           is highly auditable and flexible for complex transaction types but may require
           more computation for balance retrieval.
        2. **Snapshotting**: In combination with event sourcing, we can periodically
           save the state (snapshot) of the wallet balance to speed up balance retrieval
           by reducing the number of events to replay.
        3. **Double-Entry Ledger System**: Similar to traditional accounting, each
           transaction is recorded twice (debit and credit), which ensures data integrity
           and provides a clear audit trail. This is particularly useful for more complex
           financial systems.

        The choice of approach depends on the company's specific requirements such as:
        - Need for auditability and historical analysis.
        - Performance and scalability requirements.
        - Complexity of financial transactions.

        By using `select_for_update`, we prevent race conditions and ensure that the balance
        is accurately updated even under concurrent transactions. The custom exception
        `NegativeBalanceException` ensures that transactions resulting in a negative
        balance are not committed.
        :param args:
        :param kwargs:
        :return:
        """
        is_new = self._state.adding  # Check if this is a new transaction
        with transaction.atomic():
            if is_new:
                wallet = Wallet.objects.select_for_update().get(id=self.wallet_id)
                super().save(*args, **kwargs)
                wallet.balance += self.amount
                if wallet.balance < Decimal('0'):
                    # Expected to roll back transaction creation
                    raise NegativeBalanceException(f'Trying to set negative amount for wallet {wallet.pk}.'
                                                   f' TX data: PK - {self.pk}, amount - {self.amount}, ID - {self.txid}')
                wallet.save(update_fields=['balance'])
            else:
                super().save(*args, **kwargs)  # Just save without updating the wallet balance

    def __str__(self):
        return f'{self.id}: {self.amount}'
