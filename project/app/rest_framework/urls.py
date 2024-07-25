from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'wallets', WalletViewSet, 'wallets')
router.register(r'transactions', TransactionViewSet, 'transactions')

urlpatterns = [
    path('', include(router.urls)),
]
