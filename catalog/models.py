from typing import Any
import time
from random import randint
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator

# --- Product (abstract) ---
class Product(models.Model):
    """
    Abstract base model for all digital products in the marketplace.

    Provides common fields for:
    - Identification: id, slug, name, SKU, UPC
    - Descriptions: description, short_description, brand, vendor, category, tags
    - Pricing:
    cost_price, retail_price, sale_price, currency, stock_quantity, is_in_stock, stock_threshold
    - Physical attributes:
    weight, dimensions, origin_country, shipping_required, color, product_size, material, variant_of
    - Media: image_main, images
    - Ratings & reviews: rating_average, review_count
    - Status: is_active, is_featured, approval_status, created_at, updated_at, deleted_at

    Automatically generates a URL-friendly slug from the product name if not provided.
    """
    id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(unique=True, blank=True, max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    brand = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    sku = models.CharField(max_length=100, unique=True, verbose_name="Stock Keeping Unit")
    upc = models.CharField(max_length=100, blank=True, verbose_name="Universal Product Code")

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default='USD')
    stock_quantity = models.IntegerField(default=0)
    stock_threshold = models.IntegerField(default=5)

    weight = models.FloatField(help_text="Weight in grams (g)", null=True, blank=True)
    length = models.FloatField(help_text="Length in centimeters (cm)", null=True, blank=True)
    width = models.FloatField(help_text="Width in centimeters (cm)", null=True, blank=True)
    height = models.FloatField(help_text="Height in centimeters (cm)", null=True, blank=True)
    origin_country = models.CharField(max_length=54, blank=True)
    shipping_required = models.BooleanField(default=True)
    color = models.CharField(max_length=50, blank=True)
    product_size = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="screen size in inches / resolution"
    )
    material = models.CharField(max_length=50, blank=True)
    variant_of = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='variants'
    )

    image_main = models.URLField(blank=True)
    images = models.JSONField(default=list, blank=True)

    rating_average = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=50, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    attributes = models.JSONField(
        default=dict,
        help_text="Dynamic attributes validated against ProductType",
    )
    product_type = models.ForeignKey(
        "ProductType",
        on_delete=models.PROTECT,
        related_name="products",
    )

    @property
    def is_in_stock(self) -> bool:
        """Returns True if the product has stock available, False otherwise."""
        return self.stock_quantity > 0

    def _slug_exists(self, slug: str) -> bool:
        """Check if a given slug already exists in the database."""
        return self.__class__.objects.filter(slug=slug).exists()

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.name)
        slug = base_slug

        while self._slug_exists(slug):
            slug = f"{base_slug}-{int(time.time())}"

        return slug

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Generates a URL-friendly slug from the product name if not already set.
        (e.g., "Apple MacBook Pro" → "apple-macbook-pro").
        """
        if not self.slug or self._slug_exists(self.slug):
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)
