from rest_framework.serializers import ModelSerializer

from catalog.models import ProductType, Product
from the_app.utils.mixins import BaseSerializerMixin


class ProductTypeSerializer(BaseSerializerMixin, ModelSerializer):
    class Meta:
        model = ProductType
        fields = ['id', 'name', 'category_type', 'subcategory_type']


class ProductTypeDetailSerializer(BaseSerializerMixin, ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'


class ProductSerializer(BaseSerializerMixin, ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'currency', 'is_in_stock', 'short_description']


class ProductDetailSerializer(BaseSerializerMixin, ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
