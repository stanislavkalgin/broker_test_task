import factory
from factory.django import DjangoModelFactory
from ..models import Wallet, Transaction


class WalletFactory(DjangoModelFactory):
    class Meta:
        model = Wallet

    label = factory.Faker('word')


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = Transaction

    wallet = factory.SubFactory(WalletFactory)
    txid = factory.Faker('word')
    amount = factory.Faker('pydecimal', left_digits=10, right_digits=18, positive=True)
