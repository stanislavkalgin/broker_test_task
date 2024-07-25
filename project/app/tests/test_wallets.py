import uuid

from django.urls import reverse
from rest_framework import test

from .factories import WalletFactory, TransactionFactory
from ..models import Wallet


class CreateWalletTestCase(test.APITestCase):
    def test_creation(self):
        response = self.client.post(
            reverse('wallets-list'),
            data={
                'data': {
                    'type': 'Wallet',
                    'attributes': {
                        'label': 'mywallet1'
                    }
                }
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Wallet.objects.all().count(), 1)

    def test_creation_ignores_balance(self):
        response = self.client.post(
            reverse('wallets-list'),
            data={
                'data': {
                    'type': 'Wallet',
                    'attributes': {
                        'label': 'mywallet1',
                        'balance': 500
                    }
                }
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Wallet.objects.all().count(), 1)
        wallet = Wallet.objects.get()
        self.assertEqual(wallet.balance, 0)

    def test_creation_ignores_id(self):
        passed_uuid = uuid.uuid4()
        response = self.client.post(
            reverse('wallets-list'),
            data={
                'data': {
                    'type': 'Wallet',
                    'attributes': {
                        'label': 'mywallet1'
                    },
                    'id': str(passed_uuid)
                }
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Wallet.objects.all().count(), 1)
        wallet = Wallet.objects.get()
        self.assertNotEqual(wallet.id, passed_uuid)


class ListRetrieveWalletTestCase(test.APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wallet = WalletFactory(label='mywallet')
        WalletFactory.create_batch(14)

    def test_retrieve_method(self):
        response = self.client.get(reverse('wallets-detail', args=[self.wallet.pk]))
        self.assertEqual(response.status_code, 200)

    def test_list_method(self):
        response = self.client.get(reverse('wallets-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 10)

        response = self.client.get(f'{reverse("wallets-list")}', {"page[number]": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 5)


class FilterWalletTestCase(test.APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wallet1 = WalletFactory(label='wallet1')
        self.wallet2 = WalletFactory(label='wallet2')
        self.wallet3 = WalletFactory(label='wallet3')

    def test_filter_wallet_by_label(self):
        response = self.client.get(reverse('wallets-list'), {'filter[label]': 'wallet1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 1)
        self.assertEqual(response.json()['data'][0]['attributes']['label'], 'wallet1')


class OrderWalletTestCase(test.APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wallet1 = WalletFactory(label='wallet1')
        self.wallet2 = WalletFactory(label='wallet2')
        TransactionFactory(wallet=self.wallet1, amount=100)
        TransactionFactory(wallet=self.wallet2, amount=50)

    def test_order_wallet_by_balance_ascending(self):
        response = self.client.get(reverse('wallets-list'), {'sort': 'balance'})
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['attributes']['label'], 'wallet2')
        self.assertEqual(results[1]['attributes']['label'], 'wallet1')

    def test_order_wallet_by_balance_descending(self):
        response = self.client.get(reverse('wallets-list'), {'sort': '-balance'})
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['attributes']['label'], 'wallet1')
        self.assertEqual(results[1]['attributes']['label'], 'wallet2')

    def test_order_wallet_by_label_ascending(self):
        response = self.client.get(reverse('wallets-list'), {'sort': 'label'})
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['attributes']['label'], 'wallet1')
        self.assertEqual(results[1]['attributes']['label'], 'wallet2')

    def test_order_wallet_by_label_descending(self):
        response = self.client.get(reverse('wallets-list'), {'sort': '-label'})
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['attributes']['label'], 'wallet2')
        self.assertEqual(results[1]['attributes']['label'], 'wallet1')
