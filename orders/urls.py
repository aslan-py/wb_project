from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orders.views import (
    CartItemViewSet,
    CartView,
    CheckoutView,
)

router = DefaultRouter()
router.register('cart/items', CartItemViewSet, basename='cart-item')


urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('', include(router.urls)),
    path('cart/checkout/', CheckoutView.as_view(), name='checkout'),
]
