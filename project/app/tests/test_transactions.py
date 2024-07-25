from decimal import Decimal

from django.urls import reverse
from rest_framework import test

from .factories import WalletFactory, TransactionFactory
from ..models import Transaction


class CreateTransactionTestCase(test.APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletFactory()

    def test_creation(self):
        response = self.client.post(
            reverse('transactions-list'),
            data={
                'data': {
                    'type': 'Transaction',
                    'attributes': {
                        'txid': '1234',
                        'amount': 100
                    },
                    'relationships': {
                        'wallet': {
                            'data': {
                                'type': 'Wallet',
                                'id': str(self.wallet.id)
                            }
                        }
                    }
                }
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Transaction.objects.all().count(), 1)
        transaction = Transaction.objects.get()
        self.assertEqual(transaction.txid, '1234')
        self.assertEqual(transaction.amount, 100)

    def test_creation_requires_unique_txid(self):
        TransactionFactory(txid='1234', wallet=self.wallet)
        response = self.client.post(
            reverse('transactions-list'),
            data={
                'data': {
                    'type': 'Transaction',
                    'attributes': {
                        'txid': '1234',
                        'amount': 200
                    },
                    'relationships': {
                        'wallet': {
                            'data': {
                                'type': 'Wallet',
                                'id': str(self.wallet.id)
                            }
                        }
                    }
                }
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_creation_updates_wallet_balance(self):
        response = self.client.post(
            reverse('transactions-list'),
            data={
                'data': {
                    'type': 'Transaction',
                    'attributes': {
                        'txid': '1234',
                        'amount': 100
                    },
                    'relationships': {
                        'wallet': {
                            'data': {
                                'type': 'Wallet',
                                'id': str(self.wallet.id)
                            }
                        }
                    }
                }
            },
        )
        self.assertEqual(response.status_code, 201)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 100)

        response = self.client.post(
            reverse('transactions-list'),
            data={
                'data': {
                    'type': 'Transaction',
                    'attributes': {
                        'txid': '1235',
                        'amount': -50
                    },
                    'relationships': {
                        'wallet': {
                            'data': {
                                'type': 'Wallet',
                                'id': str(self.wallet.id)
                            }
                        }
                    }
                }
            },
        )
        self.assertEqual(response.status_code, 201)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 50)
        self.assertEqual(Transaction.objects.all().count(), 2)

        # Transaction that makes balance negative is not accepted
        response = self.client.post(
            reverse('transactions-list'),
            data={
                'data': {
                    'type': 'Transaction',
                    'attributes': {
                        'txid': '1236',
                        'amount': -100
                    },
                    'relationships': {
                        'wallet': {
                            'data': {
                                'type': 'Wallet',
                                'id': str(self.wallet.id)
                            }
                        }
                    }
                }
            },
        )
        self.assertEqual(response.status_code, 400)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 50)
        self.assertEqual(Transaction.objects.all().count(), 2)


class ListRetrieveTransactionTestCase(test.APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wallet = WalletFactory()
        self.transaction = TransactionFactory(wallet=self.wallet, txid='1234', amount=Decimal('100'))
        TransactionFactory.create_batch(14, wallet=self.wallet)

    def test_retrieve_method(self):
        response = self.client.get(reverse('transactions-detail', args=[self.transaction.pk]))
        self.assertEqual(response.status_code, 200)

    def test_list_method(self):
        response = self.client.get(reverse('transactions-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 10)

        response = self.client.get(f'{reverse("transactions-list")}', {"page[number]": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 5)


class FilterTransactionTestCase(test.APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wallet = WalletFactory()
        self.transaction1 = TransactionFactory(wallet=self.wallet, txid='txid1', amount=Decimal('100.00'))
        self.transaction2 = TransactionFactory(wallet=self.wallet, txid='txid2', amount=Decimal('200.00'))
        self.transaction3 = TransactionFactory(wallet=self.wallet, txid='txid3', amount=Decimal('-50.00'))

    def test_filter_transaction_by_txid(self):
        response = self.client.get(reverse('transactions-list'), {'filter[txid]': 'txid1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 1)
        self.assertEqual(response.json()['data'][0]['attributes']['txid'], 'txid1')


class OrderTransactionTestCase(test.APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wallet = WalletFactory()
        self.transaction1 = TransactionFactory(wallet=self.wallet, txid='txid1', amount=Decimal('100.00'))
        self.transaction2 = TransactionFactory(wallet=self.wallet, txid='txid2', amount=Decimal('50.00'))

    def test_order_transaction_by_amount_ascending(self):
        response = self.client.get(reverse('transactions-list'), {'sort': 'amount'})
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['attributes']['txid'], 'txid2')
        self.assertEqual(results[1]['attributes']['txid'], 'txid1')

    def test_order_transaction_by_amount_descending(self):
        response = self.client.get(reverse('transactions-list'), {'sort': '-amount'})
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['attributes']['txid'], 'txid1')
        self.assertEqual(results[1]['attributes']['txid'], 'txid2')

    def test_order_transaction_by_txid_ascending(self):
        response = self.client.get(reverse('transactions-list'), {'sort': 'txid'})
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['attributes']['txid'], 'txid1')
        self.assertEqual(results[1]['attributes']['txid'], 'txid2')

    def test_order_transaction_by_txid_descending(self):
        response = self.client.get(reverse('transactions-list'), {'sort': '-txid'})
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['attributes']['txid'], 'txid2')
        self.assertEqual(results[1]['attributes']['txid'], 'txid1')