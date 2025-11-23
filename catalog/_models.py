from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify
from jsonschema import Draft7Validator, SchemaError
from jsonschema import ValidationError as JSONSchemaValidationError


@dataclass(frozen=True)
class SlugConfig:
    max_length: int = 100
    uuid_suffix_length: int = 8

    @property
    def suffix_length(self) -> int:
        return self.uuid_suffix_length + 1


class SlugService:
    @staticmethod
    def ensure_base_slug_len(base: str, cfg: SlugConfig) -> str:
        allowed_len = cfg.max_length - cfg.suffix_length
        if len(base) > allowed_len:
            last_dash = base[:allowed_len].rfind("-")
            truncated = (
                base[:last_dash] if last_dash != -1 else base[:allowed_len]
            )
            truncated = truncated.strip("-")
            return truncated or "product"
        return base

    @staticmethod
    def suffix_base_slug(base: str, cfg: SlugConfig) -> str:
        uuid_suffix = uuid.uuid4().hex[: cfg.uuid_suffix_length]
        return f"{base}-{uuid_suffix}"


class SchemaValidator:
    """This will be a class for schema validation."""

    @staticmethod
    def get_validator_for_schema(schema: dict) -> Draft7Validator:
        Draft7Validator.check_schema(schema)
        return Draft7Validator(schema)

    @staticmethod
    def validate_schema(schema: dict) -> None:
        """
        Validate the JSON schema for correctness + enforce ProductType rules.
        """
        try:
            Draft7Validator.check_schema(schema)
        except SchemaError as e:
            raise DjangoValidationError({"attributes_schema": str(e)}) from e

        schema_type = schema.get("type")
        if schema_type and schema_type != "object":
            raise DjangoValidationError(
                {"attributes_schema": "Top-level type must be 'object'."}
            )

    @staticmethod
    def validate_attributes(schema: dict, attributes: Any) -> None:
        """
        Validate an attributes instance against a schema.
        """
        SchemaValidator.validate_schema(schema)

        validator = SchemaValidator.get_validator_for_schema(schema)
        validator.validate(instance=attributes)


class VariantValidator:
    @staticmethod
    def validate_chain(product_instance: "Product") -> None:
        parent = product_instance.variant_of
        seen = set()

        while parent:
            parent_key = parent.pk or id(parent)
            product_key = product_instance.pk or id(product_instance)

            if parent_key == product_key or parent_key in seen:
                raise DjangoValidationError(
                    {"variant_of": "Circular variant relationship detected."}
                )

            seen.add(parent_key)
            parent = parent.variant_of

    @staticmethod
    def validate_integrity(product_instance: "Product") -> None:
        parent = product_instance.variant_of
        if not parent:
            return

        if (
            product_instance.pk
            and parent.pk
            and product_instance.pk == parent.pk
        ):
            raise DjangoValidationError(
                {"variant_of": "A product cannot be a variant of itself."}
            )

        if parent.product_type_id != product_instance.product_type_id:
            raise DjangoValidationError(
                {"variant_of": "A variant must have the same product type as its parent."}
            )


class ProductType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=100)
    subcategory_type = models.CharField(max_length=100, blank=True)
    attributes_schema = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def clean(self, *args: Any, **kwargs: Any) -> None:
        SchemaValidator.validate_schema(self.attributes_schema)
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
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)]
    )
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)]
    )
    retail_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        max_length=3, default="EUR",
        validators=[RegexValidator(r"^[A-Z]{3}$")]
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
        "self", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="variants"
    )

    image_main = models.URLField(blank=True)
    images = models.JSONField(default=list, blank=True)

    rating_average = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    approval_status = models.CharField(
        max_length=50, choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    attributes = models.JSONField(default=dict)
    product_type = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name="products"
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["_category"]),
            models.Index(fields=["_category", "_subcategory"]),
            GinIndex(fields=["attributes"]),
        ]

    SLUG_CONFIG = SlugConfig()

    @property
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0

    @property
    def category(self) -> str:
        return self._category

    @property
    def subcategory(self) -> str:
        return self._subcategory

    def _slug_exists(self, slug: str) -> bool:
        qs = Product.objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        return qs.exists()

    def _generate_unique_slug(self) -> str:  #TODO: DI
        cfg = self.SLUG_CONFIG
        slug = slugify(self.name) or "product"
        slug = SlugService.ensure_base_slug_len(slug, cfg)

        while self._slug_exists(slug):
            slug = SlugService.suffix_base_slug(slug, cfg)
        return slug

    def _sync_categories(self) -> None:
        if not self.pk or self.category != self.product_type.category_type:
            self._category = self.product_type.category_type
        if not self.pk or self.subcategory != self.product_type.subcategory_type:
            self._subcategory = self.product_type.subcategory_type

    def clean(self) -> None:  #TODO: DI
        VariantValidator.validate_chain(self)
        VariantValidator.validate_integrity(self)

        try:
            SchemaValidator.validate_attributes(
                self.product_type.attributes_schema,
                self.attributes
            )
        except JSONSchemaValidationError as e:
            raise DjangoValidationError({"attributes": str(e)}) from e

        super().clean()

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug or self._slug_exists(self.slug):
            self.slug = self._generate_unique_slug()

        self._sync_categories()
        self.full_clean()
        super().save(*args, **kwargs)
