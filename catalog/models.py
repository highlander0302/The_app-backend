"""
Product and ProductType models with validation and slug management.

This module defines the core catalog models:

- ProductType: Defines a type of product, including category, subcategory,
  and JSON schema for attributes.
- Product: Represents a concrete product instance with pricing, stock, images, 
  variant relationships, and attribute data.

Features included:
- JSON schema validation for product attributes via SchemaValidator.
- Variant relationship integrity and cycle detection via VariantValidator.
- Unique slug generation via SlugService, with configurable max length
  and UUID suffix.
- Cached category/subcategory fields for fast database lookups and indexing.
- Approval status tracking, stock checks, and basic product metadata.
"""
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
    """
    Represents a type of product with category, subcategory, and attribute schema.

    Attributes:
        name (str): Unique name of the product type.
        category_type (str): Main category for products of this type.
        subcategory_type (str): Optional subcategory.
        attributes_schema (dict): JSON schema defining the attributes for products.

    Validators:
        SCHEMA_VALIDATOR: Validates `attributes_schema` for correctness.
    """
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
        """Validate the JSON schema for correctness before saving."""
        self.SCHEMA_VALIDATOR.validate_schema(self.attributes_schema)
        super().clean(*args, **kwargs)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Run full validation with full_clean() and save the product type."""
        self.full_clean()
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Represents a product, including details, pricing, stock, variant relationships,
    and associated product type.

    Validators and services:
        SLUG_SERVICE: Generates unique slugs.
        SCHEMA_VALIDATOR: Validates product attributes.
        VARIANT_VALIDATOR: Validates variant_of relationships.
    """
    class ApprovalStatus(models.TextChoices):
        """Represents the approval state of a product."""
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
        """Returns True if `stock_quantity > 0`."""
        return self.stock_quantity > 0

    @property
    def category(self) -> str:
        """Cached category from `product_type`. kept in Product for fast DB retrieve."""
        return self._category

    @property
    def subcategory(self) -> str:
        """Cached subcategory from `product_type`. Kept in Product for fast DB retrieve."""
        return self._subcategory

    def _sync_categories(self) -> None:
        """
        Sync the product's internal `_category` and `_subcategory` fields
        with its ProductType.

        These fields are maintained on the Product model for fast database
        queries and indexing, so lookups can be performed without a join.
        """
        if not self.pk or self.category != self.product_type.category_type:
            self._category = self.product_type.category_type
        if not self.pk or self.subcategory != self.product_type.subcategory_type:
            self._subcategory = self.product_type.subcategory_type

    def clean(self) -> None:
        """Validate variant chain, variant integrity, and attributes."""
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
        """Generate unique slug, sync categories, run full validation, and save."""
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
