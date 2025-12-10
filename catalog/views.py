from typing import Type

from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from catalog.models import ProductType, Product
from catalog.serializers import ProductTypeSerializer, ProductTypeDetailSerializer, ProductSerializer, \
    ProductDetailSerializer


class ProductTypeViewSet(ModelViewSet):
    queryset = ProductType.objects.all()

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == 'list':
            return ProductTypeSerializer
        return ProductTypeDetailSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(is_active=True)

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == 'list':
            return ProductSerializer
        return ProductDetailSerializer
