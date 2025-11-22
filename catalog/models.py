"""
Product and ProductType models for the marketplace.

This module defines:

1. ProductType
    - Represents a type of product with a dynamic JSON schema for attributes.
    - Fields:
        - name, category_type, subcategory_type
        - attributes_schema (Draft 7 JSON Schema)
    - Validates that the schema conforms to Draft 7 and is an object.

2. Product
    - Represents a concrete product instance.
    - Fields include identification, descriptions, pricing, stock, physical attributes,
    media, ratings, status, and dynamic attributes.
    - Key behaviors:
        - Auto-generates unique slug, handles collisions with UUID suffix
        - Validates dynamic attributes against ProductType schema
        - Syncs category and subcategory fields from ProductType
        - Ensures variant integrity and prevents circular variant chains
        - Tracks stock availability, ratings, and approval status

Notes:
- Slugs are truncated and suffixed with a UUID to ensure uniqueness.
- Attributes are validated using Draft 7 JSON Schema via jsonschema.Draft7Validator.
- Variant products must share the same ProductType as their parent.
- GIN indexes are applied to the attributes field for efficient JSON queries.
"""

import uuid
from typing import Any

from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify
from jsonschema import Draft7Validator, SchemaError
from jsonschema import ValidationError as JSONSchemaValidationError


class ProductType(models.Model):
    """
    Represents a type of product with a dynamic attributes schema.

    Fields:
    - name: e.g., "Laptop", "Smartphone"
    - category_type / subcategory_type
    - attributes_schema: JSON Schema (Draft 7) defining dynamic attributes and their types
    """

    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(
        max_length=100, help_text="Top-level category of the product type"
    )
    subcategory_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional subcategory",
    )
    attributes_schema = models.JSONField(
        default=dict,
        help_text="""
            JSON Schema of product attributes (Draft 7). 
            Example:
            {
                "type": "object",
                "properties": {
                    "cpu": {"type": "string"},
                    "ram": {"type": "integer"}
                },
                "required": ["cpu", "ram"]
            }
            """,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def _validate_schema(self) -> None:
        """
        Validates that `attributes_schema` conforms to Draft 7 and is an object schema.
        Raises DjangoValidationError if invalid.
        """
        try:
            Draft7Validator.check_schema(self.attributes_schema)
        except SchemaError as e:
            raise DjangoValidationError(
                {"attributes_schema": f"Invalid JSON Schema: {str(e)}"}
            ) from e

        schema_type = self.attributes_schema.get("type")
        if schema_type and schema_type != "object":
            raise DjangoValidationError(
                {"attributes_schema": "Top-level type must be 'object'."}
            )

    def clean(self, *args: Any, **kwargs: Any) -> None:
        """
        Validates the schema before full_clean.
        """
        self._validate_schema()
        super().clean(*args, **kwargs)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Runs full_clean and saves the ProductType instance.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<ProductType id={self.id!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """
    Represents a concrete product in the marketplace.

    Each product belongs to a ProductType, which defines a JSON schema for
    dynamic attributes. Attributes are validated against ProductType.attributes_schema.

    Key behaviors:
    - Auto-generates unique slug if missing or duplicate
    - Validates dynamic attributes
    - Syncs category and subcategory from ProductType
    """

    class ApprovalStatus(models.TextChoices):
        """
        Defines the possible approval statuses for Product's field `approval_status`.
        """

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
    sku = models.CharField(
        max_length=100, unique=True, verbose_name="Stock Keeping Unit"
    )
    upc = models.CharField(
        max_length=100, blank=True, verbose_name="Universal Product Code"
    )

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
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(
        max_length=3,
        default="EUR",
        validators=[
            RegexValidator(r"^[A-Z]{3}$", "Currency must be a 3-letter uppercase code.")
        ],
    )
    stock_quantity = models.IntegerField(default=0, validators=MinValueValidator(0))
    stock_threshold = models.IntegerField(
        default=5,
        validators=MinValueValidator(0),
        help_text="Minimum stock item count to trigger a notification for replenishing stock.",
    )

    weight = models.FloatField(help_text="Weight in grams (g)", null=True, blank=True)
    length = models.FloatField(
        help_text="Length in centimeters (cm)", null=True, blank=True
    )
    width = models.FloatField(
        help_text="Width in centimeters (cm)", null=True, blank=True
    )
    height = models.FloatField(
        help_text="Height in centimeters (cm)", null=True, blank=True
    )
    origin_country = models.CharField(max_length=54, blank=True)
    shipping_required = models.BooleanField(default=True)
    color = models.CharField(max_length=50, blank=True)
    product_size = models.CharField(
        max_length=50, blank=True, verbose_name="screen size in inches / resolution"
    )
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
        max_length=50,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        help_text="The current approval status of the product.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    attributes = models.JSONField(
        default=dict,
        help_text="Dynamic attributes validated against ProductType",
    )
    product_type = models.ForeignKey(
        "ProductType",
        on_delete=models.PROTECT,
        related_name="products",
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["_category"]),
            models.Index(fields=["_category", "_subcategory"]),
            GinIndex(fields=["attributes"]),
        ]

    @property
    def is_in_stock(self) -> bool:
        """Returns True if the product has stock available, False otherwise."""
        return self.stock_quantity > 0

    @property
    def category(self) -> str:
        """Ensures _cateegory is read-only."""
        return self._category

    @property
    def subcategory(self) -> str:
        """Ensures _subcateegory is read-only."""
        return self._subcategory

    def _slug_exists(self, slug: str) -> bool:
        """
        Return True if the slug exists on another instance.
        Excludes current instance (by pk).
        """
        queryset = self.__class__.objects.filter(slug=slug)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        return queryset.exists()

    class SlugConfig:
        """
        Configuration constants for generating unique product slugs.

        Attributes:
        - MAX_LENGTH: Maximum total length of the slug, including suffix.
        - UUID_SUFFIX_LENGTH: length of the UUID suffix.
        - SUFFIX_LENGTH: length of the suffix including the hyphen.
        """

        MAX_LENGTH = 100
        UUID_SUFFIX_LENGTH = 8
        SUFFIX_LENGTH = UUID_SUFFIX_LENGTH + 1

    def _ensure_base_slug_len(self, slug: str) -> str:
        """
        Ensure the base portion of the slug fits within MAX_SLUG_LENGTH
        once a UUID suffix (and hyphen) is appended. Truncates if necessary, strips hyphens,
        and falls back to 'product' if empty.

        Returns:
            A base slug short enough to safely append "-<uuid>".
        """
        allowed_len = Product.SlugConfig.MAX_LENGTH - Product.SlugConfig.SUFFIX_LENGTH
        if len(slug) > allowed_len:
            last_dash_in_allowed_len = slug[:allowed_len].rfind("-")
            truncated = (
                slug[:last_dash_in_allowed_len]
                if last_dash_in_allowed_len != -1
                else slug[:allowed_len]
            )
            truncated = truncated.strip("-")
            return truncated if truncated else "product"
        return slug

    def _generate_unique_slug(self) -> str:
        """
        Generate a unique slug for the product.

        - slugifies the product name (fallback: "Product")
        - trims the base slug so there is room for a UUID suffix
        - appends an UUID hex suffix on collision
        - regenerates suffixes until unused

        Returns:
            A unique slug string.
        """
        slug = slugify(self.name) or "Product"
        base_slug = self._ensure_base_slug_len(slug)

        while self._slug_exists(slug):
            uuid_suffix = uuid.uuid4().hex[: Product.SlugConfig.UUID_SUFFIX_LENGTH]
            slug = f"{base_slug}-{uuid_suffix}"
        return slug

    def _validate_attributes(self) -> None:
        validator = Draft7Validator(self.product_type.attributes_schema)
        validator.validate(instance=self.attributes)

    def _sync_categories(self) -> None:
        """
        Syncs _category and _subcategory fields with ProductType.
        Only updates if product_type changed or fields are empty.
        """
        if not self.pk or self.category != self.product_type.category_type:
            self._category = self.product_type.category_type

        if not self.pk or self.subcategory != self.product_type.subcategory_type:
            self._subcategory = self.product_type.subcategory_type

    def _validate_variant_chain(self) -> None:
        """
        Ensures no circular variant relationships.
        Raises DjangoValidationError if a circular chain is detected.
        """
        parent = self.variant_of
        seen = set()
        while parent:
            if parent.id == self.id or parent.id in seen:
                raise DjangoValidationError(
                    {"variant_of": "Circular variant relationship detected."}
                )
            seen.add(parent.id)
            parent = parent.variant_of

    def _validate_variant_integrity(self) -> None:
        """
        Ensures variant integrity:
        - A product cannot be a variant of itself.
        - A variant must have the same ProductType as its parent.
        Raises DjangoValidationError if invalid.
        """
        if self.variant_of:
            if self.variant_of_id and self.pk and self.variant_of_id == self.pk:
                raise DjangoValidationError(
                    {"variant_of": "A product cannot be a variant of itself."}
                )
            if self.variant_of.product_type_id != self.product_type_id:
                raise DjangoValidationError(
                    {
                        "variant_of": "A variant must have the same product type as its parent."
                    }
                )

    def clean(self) -> None:
        """
        Custom model validation.
        - Validates `attributes` against `product_type.attributes_schema` JSON Schema.
        - Raises `DjangoValidationError` if attributes are invalid.
        - Prevents a product from being a variant of itself or circular variant chains.
        - Ensures variant products have the same ProductType as the parent.
        """
        self._validate_variant_chain()
        self._validate_variant_integrity()

        try:
            self._validate_attributes()
        except JSONSchemaValidationError as e:
            raise DjangoValidationError({"attributes": str(e)}) from e

        super().clean()

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Save the Product instance.

        - Generates a unique slug if missing or duplicate.
        - Syncs Product category/subcategory fields with ProductType category/subcategory.
        - Calls full_clean() and saves the object.
        """

        if not self.slug or self._slug_exists(self.slug):
            self.slug = self._generate_unique_slug()

        self._sync_categories()

        self.full_clean()

        super().save(*args, **kwargs)
