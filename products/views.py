from rest_framework.viewsets import ModelViewSet

from products.models import Product
from products.permissions import IsAdminOrReadOnly
from products.schema import product_schema
from products.serializers import ProductSerializer


@product_schema
class ProductViewSet(ModelViewSet):
    """CRUD по товарам: читают все, изменяет только администратор."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrReadOnly,)
