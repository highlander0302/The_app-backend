from __future__ import annotations

from typing import Any

from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from jsonschema import ValidationError as JSONSchemaValidationError

from catalog.services.slug_service import SlugConfig, SlugService
from catalog.services.validators.schema import SchemaValidator
from catalog.services.validators.variant import VariantValidator


class ProductType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=100)
    subcategory_type = models.CharField(max_length=100, blank=True)
    attributes_schema = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    SCHEMA_VALIDATOR = SchemaValidator

    def clean(self, *args: Any, **kwargs: Any) -> None:
        self.SCHEMA_VALIDATOR.validate_schema(self.attributes_schema)
        super().clean(*args, **kwargs)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class Product(models.Model):
    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        ARCHIVED = "archived", "Archived"

    slug = models.SlugField(unique=True, blank=True, max_length=100)
    name = models.CharField(max_length=255)

    _category = models.CharField(max_length=100, blank=True, editable=False)
    _subcategory = models.CharField(max_length=100, blank=True, editable=False)

    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    brand = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    upc = models.CharField(max_length=100, blank=True)

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
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
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        max_length=3, default="EUR", validators=[RegexValidator(r"^[A-Z]{3}$")]
    )
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_threshold = models.IntegerField(default=5, validators=[MinValueValidator(0)])

    weight = models.FloatField(null=True, blank=True)
    length = models.FloatField(null=True, blank=True)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)

    origin_country = models.CharField(max_length=54, blank=True)
    shipping_required = models.BooleanField(default=True)
    color = models.CharField(max_length=50, blank=True)
    product_size = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=50, blank=True)

    variant_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="variants",
    )

    image_main = models.URLField(blank=True)
    images = models.JSONField(default=list, blank=True)

    rating_average = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    approval_status = models.CharField(
        max_length=50, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    attributes = models.JSONField(default=dict)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT, related_name="products")

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["_category"]),
            models.Index(fields=["_category", "_subcategory"]),
            GinIndex(fields=["attributes"]),
        ]

    SLUG_CONFIG = SlugConfig()
    SLUG_SERVICE = SlugService(SLUG_CONFIG)
    SCHEMA_VALIDATOR = SchemaValidator
    VARIANT_VALIDATOR = VariantValidator

    @property
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0

    @property
    def category(self) -> str:
        return self._category

    @property
    def subcategory(self) -> str:
        return self._subcategory

    def _sync_categories(self) -> None:
        if not self.pk or self.category != self.product_type.category_type:
            self._category = self.product_type.category_type
        if not self.pk or self.subcategory != self.product_type.subcategory_type:
            self._subcategory = self.product_type.subcategory_type

    def clean(self) -> None:
        self.VARIANT_VALIDATOR.validate_chain(self)
        self.VARIANT_VALIDATOR.validate_integrity(self)

        try:
            self.SCHEMA_VALIDATOR.validate_attributes(
                self.product_type.attributes_schema, self.attributes
            )
        except JSONSchemaValidationError as e:
            raise DjangoValidationError({"attributes": str(e)}) from e

        super().clean()

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug or self.SLUG_SERVICE.slug_exists(
            model_class=type(self),
            slug=self.slug,
            exclude_pk=self.pk,
        ):
            self.slug = self.SLUG_SERVICE.generate_unique_slug(
                model_class=type(self),
                name=self.name,
                exclude_pk=self.pk,
            )
        self._sync_categories()
        self.full_clean()
        super().save(*args, **kwargs)
