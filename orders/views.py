from decimal import Decimal

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from orders.models import CartItem
from orders.schema import cart_item_schema, cart_schema, checkout_schema
from orders.serializers import (
    CartItemSerializer,
    OrderSerializer,
)
from orders.services import checkout


@cart_schema
class CartView(APIView):
    """Просмотр корзины текущего пользователя: позиции и итоговая сумма."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        """Возвращает позиции корзины и их суммарную стоимость."""
        items = CartItem.objects.filter(user=request.user).select_related(
            'product'
        )
        total_price = sum(
            (item.product.price * item.quantity for item in items),
            Decimal('0.00'),
        )
        return Response({
            'items': CartItemSerializer(items, many=True).data,
            'total_price': total_price,
        })


@cart_item_schema
class CartItemViewSet(ModelViewSet):
    """Позиции корзины: список, добавление, изменение количества, удаление."""

    # queryset нужен только для вывода типа id в схеме; реальную
    # выборку задаёт get_queryset.
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self) -> QuerySet[CartItem]:
        """Только позиции корзины текущего пользователя."""
        return CartItem.objects.filter(user=self.request.user).select_related(
            'product'
        )

    def perform_create(self, serializer: CartItemSerializer) -> None:
        """Привязывает позицию к корзине текущего пользователя."""
        serializer.save(user=self.request.user)


@checkout_schema
class CheckoutView(APIView):
    """Оформление заказа из корзины."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        """Оформляет заказ и возвращает его данные."""
        order = checkout(request.user)
        return Response(
            OrderSerializer(order).data, status=status.HTTP_201_CREATED
        )
