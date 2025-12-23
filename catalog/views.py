from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from catalog.models import ProductType, Product
from catalog.serializers import ProductTypeSerializer, ProductTypeDetailSerializer, ProductSerializer, \
    ProductDetailSerializer


class ProductTypeViewSet(ModelViewSet):
    """
    ViewSet for ProductType CRUD operations.

    - `list` action returns a simplified representation of product types.
    - All other actions use a detailed serializer.
    """
    queryset = ProductType.objects.all()

    def get_serializer_class(self) -> type[ModelSerializer]:
        if self.action == 'list':
            return ProductTypeSerializer
        return ProductTypeDetailSerializer


class ProductViewSet(ModelViewSet):
    """
    ViewSet for Product CRUD operations.

    - `list` action returns a simplified representation of products.
    - All other actions use a detailed serializer.
    """
    queryset = Product.objects.filter(is_active=True)

    def get_serializer_class(self) -> type[ModelSerializer]:
        if self.action == 'list':
            return ProductSerializer
        return ProductDetailSerializer
