from rest_framework.routers import DefaultRouter

from catalog.views import ProductViewSet, ProductTypeViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-types', ProductTypeViewSet, basename='product-type')

urlpatterns = router.urls
