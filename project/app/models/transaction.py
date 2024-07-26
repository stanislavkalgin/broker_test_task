import uuid
from decimal import Decimal

from django.db import models, transaction
from django.db.models import Sum

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
        This method implements a hybrid approach, combining a ledger-based system with precomputed balances.
        Here, each transaction is recorded in the Transaction table, and the wallet's balance is updated in real-time.

        Key Features:
        - **Atomic Transactions**: Using `transaction.atomic()` to ensure that all database operations within the block
          are completed successfully or rolled back entirely to maintain consistency.
        - **Row Locking**: `select_for_update()` is employed to lock the wallet record, preventing race conditions
          and ensuring accurate balance updates even under concurrent transactions.
        - **Integrity Checks**: The custom exception `NegativeBalanceException` ensures that transactions resulting in
          a negative balance are not committed, maintaining the integrity of wallet balances.

        Alternative Approaches:
        - **Ledger-Based System**: Calculate the balance on-the-fly by summing all transactions related to a wallet.
          This approach offers high accuracy and traceability but can be slower for wallets with a large number of transactions.
        - **Precomputed Balance with Periodic Reconciliation**: Maintain a precomputed balance that is updated in real-time
          and periodically reconcile with the transaction log to ensure accuracy. This balances performance and consistency.
        - **Event Sourcing**: Store events representing transactions and other changes, deriving the current state (balance)
          from these events. This provides high flexibility and traceability but requires a more complex infrastructure.
        - **Blockchain and Distributed Ledger Technology (DLT)**: Record transactions on a blockchain, using smart contracts
          to automate balance updates and enforce rules. This approach offers high security and immutability but can be
          resource-intensive and complex to implement.

        By using this hybrid approach, we aim to balance performance, accuracy, and complexity, ensuring fast balance
        retrieval and consistent updates through atomic transactions and integrity checks.

        :param args:
        :param kwargs:
        :return:
        """
        is_new = self._state.adding  # Check if this is a new transaction
        with transaction.atomic():
            if is_new:
                wallet = Wallet.objects.select_for_update().get(id=self.wallet_id)
                super().save(*args, **kwargs)
                wallet.balance = Transaction.objects.filter(wallet=wallet).aggregate(amount=Sum('amount')).get('amount')
                if wallet.balance < Decimal('0'):
                    # Expected to roll back transaction creation
                    raise NegativeBalanceException(f'Trying to set negative amount for wallet {wallet.pk}.'
                                                   f' TX data: PK - {self.pk}, amount - {self.amount}, ID - {self.txid}')
                wallet.save(update_fields=['balance'])
            else:
                super().save(*args, **kwargs)  # Just save without updating the wallet balance

    def __str__(self):
        return f'{self.id}: {self.amount}'
