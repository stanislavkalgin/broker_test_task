from rest_framework import viewsets, exceptions, mixins

from ..exceptions import NegativeBalanceException
from ..models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer


class WalletViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    """
    Once created, a wallet cannot be deleted or updated. Label can be used in outer systems or by clients
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    ordering_fields = ['created_at', 'label', 'balance']
    ordering = '-created_at'
    filterset_fields = ['label']


class TransactionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    """
    Once created, a transaction cannot be deleted or updated. TXID can be used in outer systems or by clients.
    Amount is a write-only-once-field
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    ordering_fields = ['created_at', 'txid', 'amount']
    ordering = '-created_at'
    filterset_fields = ['txid', 'wallet__label']

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except NegativeBalanceException:
            raise exceptions.ValidationError('Creating this transaction will set negative amount on wallet')
